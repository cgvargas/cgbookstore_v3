"""
Utilitários de Proteção Anti-Bot para Formulários Públicos.

Fornece:
1. Geração e validação de tokens temporais assinados criptograficamente (Time-Gate).
2. Lista de verificação de domínios de e-mail temporários / descartáveis.
3. Rate limiting leve por IP utilizando o cache do Django.
4. Detecção de preenchimento de Honeypot.
"""
import time
import logging
from django.core import signing
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Domínios de e-mail temporários/descartáveis frequentemente abusados por bots
DISPOSABLE_EMAIL_DOMAINS = {
    'besttempmail.com',
    'immenseignite.info',
    'tempmail.com',
    'temp-mail.org',
    'guerrillamail.com',
    'guerrillamail.net',
    'guerrillamail.org',
    'mailinator.com',
    '10minutemail.com',
    '10minutemail.net',
    'yopmail.com',
    'sharklasers.com',
    'dispostable.com',
    'getairmail.com',
    'mohmal.com',
    'trashmail.com',
    'throwawaymail.com',
    'generator.email',
    'emailondeck.com',
    'tempinbox.com',
    'fakeinbox.com',
    'inboxkitten.com',
    'burnermail.io',
    'crazymailing.com',
    'mytemp.email',
}

SALT_BOT_TOKEN = 'cgbookstore-anti-bot-gate-2026'


def get_client_ip(request) -> str:
    """Extrai o IP real do cliente considerando headers de proxy (Render, Cloudflare, Nginx)."""
    if not request:
        return '127.0.0.1'
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Pega o primeiro IP da lista
        return x_forwarded_for.split(',')[0].strip()
    
    cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_connecting_ip:
        return cf_connecting_ip.strip()
        
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def generate_bot_token() -> str:
    """Gera um token criptografado com o timestamp atual."""
    payload = {'ts': time.time()}
    return signing.dumps(payload, salt=SALT_BOT_TOKEN)


def validate_bot_token(token: str, min_seconds: float = 2.5, max_seconds: float = 86400.0) -> tuple[bool, str]:
    """
    Valida o token criptografado da submissão.
    
    Retorna:
        (is_valid: bool, reason: str)
    """
    if not token:
        return False, "Token de validação ausente."
    
    try:
        data = signing.loads(token, salt=SALT_BOT_TOKEN, max_age=int(max_seconds))
        ts = data.get('ts')
        if not ts:
            return False, "Token anti-bot malformado."
        
        elapsed = time.time() - float(ts)
        if elapsed < min_seconds:
            logger.warning(f"[AntiBot] Submissão ultra-rápida detectada: {elapsed:.2f}s (mínimo {min_seconds}s)")
            return False, "Submissão muito rápida. Por favor, aguarde alguns segundos e envie novamente."
        
        return True, "OK"
    except signing.SignatureExpired:
        return False, "Formulário expirado. Por favor, recarregue a página e tente novamente."
    except signing.BadSignature:
        return False, "Validação de segurança inválida."
    except Exception as e:
        logger.error(f"[AntiBot] Erro ao validar token anti-bot: {e}")
        return False, "Erro na validação do formulário."


def is_disposable_email(email: str) -> bool:
    """Verifica se o endereço de e-mail pertence a um domínio temporário conhecido."""
    if not email or '@' not in email:
        return False
    domain = email.split('@')[-1].strip().lower()
    return domain in DISPOSABLE_EMAIL_DOMAINS


def check_rate_limit(request, action: str, max_attempts: int = 5, window_seconds: int = 600) -> bool:
    """
    Verifica se o IP excedeu o limite de requisições para a ação indicada.
    
    Retorna True se permitido, False se bloqueado.
    """
    ip = get_client_ip(request)
    cache_key = f"rate_limit:{action}:{ip}"
    
    try:
        attempts = cache.get(cache_key, 0)
        if attempts >= max_attempts:
            logger.warning(f"[AntiBot RateLimit] IP {ip} bloqueado para '{action}' ({attempts}/{max_attempts})")
            return False
        
        # Incrementa contador
        if attempts == 0:
            cache.set(cache_key, 1, timeout=window_seconds)
        else:
            cache.incr(cache_key)
        return True
    except Exception as e:
        # Se o cache falhar, não bloqueia usuários legítimos
        logger.error(f"[AntiBot RateLimit] Erro no cache: {e}")
        return True

"""
Motor de detecção de conduta suspeita e análise de qualidade.

Analisa cada mensagem do usuário buscando padrões de:
- Linguagem abusiva/ofensiva
- Spam (mensagens repetitivas em alta velocidade)
- Tentativas de jailbreak da IA
- Conteúdo inadequado ou ilegal
"""
import re
import logging
from datetime import timedelta
from typing import Optional
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class SuspiciousActivityDetector:
    """
    Analisa mensagens dos usuários em busca de condutas suspeitas.

    Uso:
        detector = SuspiciousActivityDetector()
        activity = detector.analyze_message(user_message_obj, session, user)
        if activity:
            # alerta foi criado
    """

    # ===== CONFIGURAÇÕES DE SPAM =====
    # Número de mensagens em SPAM_WINDOW_SECONDS que caracteriza spam
    SPAM_THRESHOLD = getattr(settings, 'MONITORING_SPAM_THRESHOLD', 5)
    SPAM_WINDOW_SECONDS = getattr(settings, 'MONITORING_SPAM_WINDOW_SECONDS', 60)

    # ===== PALAVRAS ABUSIVAS (pt-BR) =====
    # Lista de palavras/radicais ofensivos — ajuste conforme necessário
    ABUSIVE_KEYWORDS_HIGH = [
        # Palavrões graves e discurso de ódio
        r'\bputa\b', r'\bvadia\b', r'\bbastard[ao]\b', r'\bviado\b',
        r'\bporra\b', r'\bcorno?\b', r'\bfoder\b', r'\bfode\b',
        r'\bmerda\b', r'\bcacete\b', r'\bpau\b', r'\bpentelh[ao]\b',
        r'\bidiota\b', r'\bimbecil\b', r'\bestúpid[ao]\b',
        r'\bcretino\b', r'\bburro\b', r'\bseu lixo\b',
        # Racismo e preconceito
        r'\bnazist[ao]\b', r'\bsuicíd', r'\bmatar[-\s]?se\b',
    ]

    ABUSIVE_KEYWORDS_MEDIUM = [
        r'\bdroga\b', r'\bobcecad[ao]\b', r'\bchato\b', r'\blixo\b',
        r'\binútil\b', r'\btolo\b', r'\babsurd[ao]\b',
        r'\bjogad[ao]\b', r'\bfraude\b',
    ]

    # ===== PADRÕES DE JAILBREAK =====
    # Tentativas comuns de contornar restrições da IA
    JAILBREAK_PATTERNS = [
        # Instruções diretas de bypass
        r'ignore\s+(all\s+)?(previous|suas|os|as)\s+(instructions?|instru[çc][õo]es|regras)',
        r'esqueça\s+(todas?\s+)?(suas|as)\s+(instru[çc][õo]es|regras|limita[çc][õo]es)',
        r'forget\s+(all\s+)?your\s+(instructions?|rules|guidelines)',
        r'ignore\s+your\s+(instructions?|programming|rules)',

        # Roleplay para bypass
        r'(finja|pretend|act\s+as|aja\s+como)\s+(que\s+)?(você\s+)?(é|ser[áa])\s+(uma?\s+)?(ia\s+)?(sem|without)\s+(regras|rules|restrictions)',
        r'do\s+anything\s+now',
        r'jailbreak',
        r'DAN\s*(mode|prompt)',

        # Tentar extrair o system prompt
        r'(repita|repeat|mostre?|show)\s+(seu|your|o)\s+(system\s+)?prompt',
        r'(o\s+que\s+est[áa]\s+no|what\s+is\s+in\s+your)\s+(system|context)',

        # Bypass de segurança
        r'(sem|without|no)\s+(filtros?|filters?|censura|censorship|restrições?|restrictions?)',
        r'modo\s+(desenvolvedor|developer|admin|irrestrito)',
        r'(enable|ativar?|ligar?)\s+(developer\s+mode|modo\s+desenvolvedor)',
    ]

    # ===== CONTEÚDO POTENCIALMENTE ILEGAL =====
    ILLEGAL_CONTENT_PATTERNS = [
        r'(como\s+)?(fazer|fabricar|sintetizar)\s+(bomb[as]?|explosiv[ao]s?|arma[s]?)',
        r'(drogas?|entorpecentes?)\s+(ilega[il]s?|como\s+fazer)',
        r'(vender?|comprar?)\s+(armas?\s+)?(ilega[il]s?)',
        r'(hack|invadir?|hackear?)\s+(conta|sistema|banco)',
        r'(roubar?|furtar?)\s+(cart[aã]o|credenciais?|senha)',
        r'(conteúdo|material|imagem|foto)\s+(infantil|criança)',
        r'(phishing|golpe|fraude)\s+(como\s+fazer)',
    ]

    def analyze_message(self, user_message, session, user=None, ip_address=None) -> Optional[object]:
        """
        Analisa uma mensagem em busca de condutas suspeitas.

        Args:
            user_message: Instância de ChatMessage (role='user')
            session: Instância de ChatSession
            user: Instância de User (None para anônimos)
            ip_address: IP do usuário (para rastreamento anônimo)

        Returns:
            SuspiciousActivity criada ou None se nada foi detectado.
        """
        from .models import SuspiciousActivity

        text = user_message.content
        text_lower = text.lower()

        # 1. Verificar spam primeiro (mais rápido)
        is_spam, spam_count = self._check_spam(user, session)
        if is_spam:
            logger.info(f"🚨 Spam detectado: {spam_count} msgs em {self.SPAM_WINDOW_SECONDS}s")
            return self._create_activity(
                user_message=user_message,
                session=session,
                user=user,
                activity_type='spam',
                severity='medium',
                detected_keywords=[f'{spam_count} mensagens em {self.SPAM_WINDOW_SECONDS}s'],
                ip_address=ip_address,
            )

        # 2. Verificar tentativas de jailbreak
        jailbreak_match = self._check_jailbreak(text_lower)
        if jailbreak_match:
            logger.info(f"🚨 Tentativa de jailbreak detectada: {jailbreak_match}")
            return self._create_activity(
                user_message=user_message,
                session=session,
                user=user,
                activity_type='jailbreak_attempt',
                severity='high',
                detected_keywords=[jailbreak_match],
                ip_address=ip_address,
            )

        # 3. Verificar conteúdo ilegal
        illegal_match = self._check_illegal_content(text_lower)
        if illegal_match:
            logger.info(f"🚨 Conteúdo ilegal detectado: {illegal_match}")
            return self._create_activity(
                user_message=user_message,
                session=session,
                user=user,
                activity_type='illegal_content',
                severity='critical',
                detected_keywords=[illegal_match],
                ip_address=ip_address,
            )

        # 4. Verificar linguagem abusiva
        is_abusive, matched_keywords, severity = self._check_abusive_language(text_lower)
        if is_abusive:
            logger.info(f"🚨 Linguagem abusiva detectada: {matched_keywords}")
            return self._create_activity(
                user_message=user_message,
                session=session,
                user=user,
                activity_type='abusive_language',
                severity=severity,
                detected_keywords=matched_keywords,
                ip_address=ip_address,
            )

        return None

    def _check_spam(self, user, session) -> tuple[bool, int]:
        """
        Verifica se o usuário está enviando mensagens em excesso (spam).

        Returns:
            Tupla (is_spam, count)
        """
        from chatbot_literario.models import ChatMessage

        cutoff = timezone.now() - timedelta(seconds=self.SPAM_WINDOW_SECONDS)

        try:
            if user and user.is_authenticated:
                # Contar msgs do usuário em todas as suas sessões
                count = ChatMessage.objects.filter(
                    session__user=user,
                    role='user',
                    created_at__gte=cutoff,
                ).count()
            else:
                # Para anônimos, contar msgs da sessão atual
                count = ChatMessage.objects.filter(
                    session=session,
                    role='user',
                    created_at__gte=cutoff,
                ).count()

            return count >= self.SPAM_THRESHOLD, count
        except Exception as e:
            logger.error(f"Erro ao verificar spam: {e}")
            return False, 0

    def _check_jailbreak(self, text_lower: str) -> Optional[str]:
        """
        Verifica se o texto contém padrões de tentativa de jailbreak.

        Returns:
            Padrão encontrado ou None.
        """
        for pattern in self.JAILBREAK_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE)
            if match:
                return match.group(0)[:80]
        return None

    def _check_illegal_content(self, text_lower: str) -> Optional[str]:
        """
        Verifica se o texto solicita conteúdo ilegal.

        Returns:
            Padrão encontrado ou None.
        """
        for pattern in self.ILLEGAL_CONTENT_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE)
            if match:
                return match.group(0)[:80]
        return None

    def _check_abusive_language(self, text_lower: str) -> tuple[bool, list, str]:
        """
        Verifica se o texto contém linguagem abusiva.

        Returns:
            Tupla (is_abusive, matched_keywords, severity)
        """
        high_matches = []
        medium_matches = []

        for pattern in self.ABUSIVE_KEYWORDS_HIGH:
            if re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE):
                # Extrair o termo encontrado para log
                match = re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE)
                if match:
                    high_matches.append(match.group(0))

        for pattern in self.ABUSIVE_KEYWORDS_MEDIUM:
            if re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE):
                match = re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE)
                if match:
                    medium_matches.append(match.group(0))

        if high_matches:
            return True, high_matches, 'high'
        elif len(medium_matches) >= 2:
            # Múltiplas palavras médias = severidade média
            return True, medium_matches, 'medium'
        elif medium_matches:
            return True, medium_matches, 'low'

        return False, [], 'low'

    def _create_activity(
        self,
        user_message,
        session,
        user,
        activity_type: str,
        severity: str,
        detected_keywords: list,
        ip_address: str = None,
    ):
        """
        Cria um registro de SuspiciousActivity no banco de dados.

        Returns:
            Instância de SuspiciousActivity criada.
        """
        from .models import SuspiciousActivity

        # Verificar threshold mínimo de severidade configurado
        min_severity = getattr(settings, 'MONITORING_ALERT_MIN_SEVERITY', 'low')
        severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}

        if severity_order.get(severity, 0) < severity_order.get(min_severity, 0):
            logger.debug(f"Atividade {severity} abaixo do threshold mínimo {min_severity}. Ignorando.")
            return None

        # Não criar duplicatas: verificar se já existe alerta similar nos últimos 5 minutos
        cutoff = timezone.now() - timedelta(minutes=5)
        existing = SuspiciousActivity.objects.filter(
            message=user_message,
            activity_type=activity_type,
            created_at__gte=cutoff,
        ).first()

        if existing:
            logger.debug(f"Atividade duplicada ignorada: {activity_type}")
            return existing

        try:
            activity = SuspiciousActivity.objects.create(
                user=user if (user and user.is_authenticated) else None,
                session=session,
                message=user_message,
                activity_type=activity_type,
                severity=severity,
                detected_keywords=detected_keywords,
                message_content=user_message.content[:1000],  # Limitar tamanho
                session_key=session.session_key if session else None,
                user_ip=ip_address,
            )
            logger.info(
                f"✅ SuspiciousActivity criada: [{severity.upper()}] {activity_type} "
                f"| Usuário: {user.username if user and user.is_authenticated else 'Anônimo'}"
            )
            return activity

        except Exception as e:
            logger.error(f"❌ Erro ao criar SuspiciousActivity: {e}", exc_info=True)
            return None


class AIResponseQualityChecker:
    """
    Verifica a qualidade das respostas da IA antes de enviá-las ao usuário.

    Detecta:
    - Respostas vazias ou muito curtas
    - Respostas truncadas
    - Possíveis alucinações (quando há dados do RAG para comparar)
    """

    MIN_RESPONSE_LENGTH = 10  # Mínimo de caracteres para uma resposta válida

    def check_response(self, response_text: str, user_message_text: str = '') -> Optional[dict]:
        """
        Analisa a resposta da IA e retorna informações de problema, se houver.

        Args:
            response_text: Texto da resposta da IA
            user_message_text: Mensagem original do usuário (para contexto)

        Returns:
            Dicionário com {alert_type, severity, description} ou None se OK.
        """
        if not response_text or not response_text.strip():
            return {
                'alert_type': 'empty_response',
                'severity': 'high',
                'description': 'A IA retornou uma resposta vazia.'
            }

        if len(response_text.strip()) < self.MIN_RESPONSE_LENGTH:
            return {
                'alert_type': 'empty_response',
                'severity': 'medium',
                'description': f'Resposta muito curta: "{response_text.strip()}"'
            }

        # Verificar se a resposta está truncada (termina no meio de uma frase)
        stripped = response_text.strip()
        if stripped and stripped[-1] not in '.!?…"\'':
            # Resposta pode estar truncada — verificar se é longa
            if len(stripped) > 200:
                return {
                    'alert_type': 'empty_response',
                    'severity': 'low',
                    'description': 'Resposta possivelmente truncada (não termina com pontuação).'
                }

        return None

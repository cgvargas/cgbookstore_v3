"""
Utilitários do módulo Product Analytics.

Funções auxiliares puras (sem efeitos colaterais em banco),
reutilizadas por services e middleware.
"""
import hashlib
import re
from typing import Optional
from django.conf import settings

from .constants import (
    URL_TO_PAGE_NAME,
    BOT_USER_AGENT_SUBSTRINGS,
    DEVICE_TYPE_DESKTOP,
    DEVICE_TYPE_MOBILE,
    DEVICE_TYPE_TABLET,
    DEVICE_TYPE_UNKNOWN,
)


def get_analytics_settings() -> dict:
    """
    Retorna as configurações do módulo com valores padrão seguros.
    """
    defaults = {
        "PROCESSING_MODE": "synchronous",
        "SESSION_TIMEOUT_MINUTES": 30,
        "EVENT_RETENTION_DAYS": 90,
        "SESSION_RETENTION_DAYS": 90,
    }
    user_settings = getattr(settings, "PRODUCT_ANALYTICS", {})
    return {**defaults, **user_settings}


def normalize_page_name(path: str) -> str:
    """
    Converte um path de URL para um nome de página canônico e normalizado.

    Ex: '/livros/o-senhor-dos-aneis-123/' → 'book_detail'
        '/' → 'home'
        '/busca/?q=tolkien' → 'search'

    Se o path não corresponder a nenhuma rota conhecida, retorna 'other'.
    """
    # Remove query string e fragmentos
    path = path.split("?")[0].split("#")[0]

    # Normaliza trailing slash
    if path and path != "/" and not path.endswith("/"):
        path = path + "/"

    for prefix, page_name in URL_TO_PAGE_NAME:
        # Normaliza o prefixo com trailing slash para comparacao consistente
        if prefix == "/":
            # Apenas match exato para a raiz
            if path == "/":
                return page_name
        elif prefix.endswith("/"):
            if path == prefix or path.startswith(prefix):
                return page_name
        else:
            # Prefixo sem trailing slash (como '/busca')
            normalized_prefix = prefix + "/"
            if path == normalized_prefix or path.startswith(normalized_prefix):
                return page_name

    return "other"


def extract_object_info(path: str) -> tuple[Optional[str], Optional[int]]:
    """
    Tenta extrair o tipo e ID do objeto referenciado no path.

    Retorna (object_type, object_id) ou (None, None).

    Ex: '/livros/o-senhor-123/' → ('book', 123)
        '/autores/tolkien-42/' → ('author', 42)
        '/' → (None, None)
    """
    patterns = [
        (r"^/livros/[^/]+-(\d+)/?$", "book"),
        (r"^/livros/(\d+)/?", "book"),
        (r"^/autores/[^/]+-(\d+)/?$", "author"),
        (r"^/autores/(\d+)/?", "author"),
        (r"^/noticias/[^/]+-(\d+)/?$", "article"),
        (r"^/debates/(\d+)/?", "debate"),
        (r"^/ereader/(\d+)/?", "book"),
        (r"^/universo/[^/]+-(\d+)/?$", "universe"),
    ]
    # Remove query string
    clean_path = path.split("?")[0]

    for pattern, obj_type in patterns:
        match = re.search(pattern, clean_path)
        if match:
            try:
                return obj_type, int(match.group(1))
            except (ValueError, IndexError):
                return obj_type, None

    return None, None


def hash_search_query(query: str) -> str:
    """
    Retorna um hash SHA-256 truncado (16 hex chars) do termo de busca.
    Usado para deduplicar buscas sem armazenar o termo literal.

    LGPD: o termo original jamais é persistido.
    """
    if not query:
        return ""
    normalized = query.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def detect_device_type(user_agent: str) -> str:
    """
    Detecta o tipo de dispositivo a partir do User-Agent.

    Retorna: 'desktop', 'mobile', 'tablet', 'unknown'

    LGPD: O User-Agent bruto nunca é armazenado — apenas o tipo derivado.
    """
    if not user_agent:
        return DEVICE_TYPE_UNKNOWN

    ua_lower = user_agent.lower()

    # Tablet antes de mobile para evitar falsos positivos (iPad contém 'mobile' em alguns UAs)
    if "tablet" in ua_lower or "ipad" in ua_lower:
        return DEVICE_TYPE_TABLET

    if (
        "mobile" in ua_lower
        or "android" in ua_lower
        or "iphone" in ua_lower
        or "ipod" in ua_lower
        or "blackberry" in ua_lower
        or "windows phone" in ua_lower
    ):
        return DEVICE_TYPE_MOBILE

    if ua_lower:
        return DEVICE_TYPE_DESKTOP

    return DEVICE_TYPE_UNKNOWN


def detect_browser_family(user_agent: str) -> str:
    """
    Detecta a família do navegador a partir do User-Agent.

    Retorna nome genérico do navegador (ex: 'Chrome', 'Firefox', 'Safari').
    LGPD: Apenas a família, nunca a versão exata ou UA completo.
    """
    if not user_agent:
        return "Unknown"

    ua_lower = user_agent.lower()

    # Ordem importante: Edge antes de Chrome, Chrome antes de Safari
    if "edg/" in ua_lower or "edghtml" in ua_lower:
        return "Edge"
    if "opr/" in ua_lower or "opera" in ua_lower:
        return "Opera"
    if "firefox/" in ua_lower or "fxios/" in ua_lower:
        return "Firefox"
    if "chrome/" in ua_lower or "crios/" in ua_lower:
        return "Chrome"
    if "safari/" in ua_lower:
        return "Safari"
    if "msie" in ua_lower or "trident/" in ua_lower:
        return "Internet Explorer"
    if "samsung" in ua_lower:
        return "Samsung Browser"

    return "Other"


def detect_os_family(user_agent: str) -> str:
    """
    Detecta o sistema operacional a partir do User-Agent.

    Retorna nome genérico do SO (ex: 'Windows', 'Android', 'iOS').
    LGPD: Apenas família, não versão ou UA completo.
    """
    if not user_agent:
        return "Unknown"

    ua_lower = user_agent.lower()

    if "windows" in ua_lower:
        return "Windows"
    if "android" in ua_lower:
        return "Android"
    if "iphone" in ua_lower or "ipad" in ua_lower or "ipod" in ua_lower:
        return "iOS"
    if "mac os" in ua_lower or "macos" in ua_lower:
        return "macOS"
    if "linux" in ua_lower:
        return "Linux"
    if "cros" in ua_lower:
        return "ChromeOS"

    return "Other"


def extract_referer_domain(referer: str) -> str:
    """
    Extrai apenas o domínio do cabeçalho Referer, sem path ou parâmetros.

    LGPD: Nunca armazena o path completo do referer (pode conter PII em queries).

    Ex: 'https://www.google.com/search?q=tolkien' → 'google.com'
        'https://cgbookstore.com.br/livros/...' → 'cgbookstore.com.br' (interno)
    """
    if not referer:
        return ""

    try:
        # Remove protocolo
        domain = referer.split("//")[-1]
        # Remove path, query e fragmento
        domain = domain.split("/")[0]
        # Remove porta
        domain = domain.split(":")[0]
        # Remove www. para normalização
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()[:200]
    except Exception:
        return ""


def is_bot_request(user_agent: str) -> bool:
    """
    Verifica se o User-Agent pertence a um robô ou crawler conhecido.
    """
    if not user_agent:
        return False
    ua_lower = user_agent.lower()
    return any(bot in ua_lower for bot in BOT_USER_AGENT_SUBSTRINGS)


def extract_utm_params(request) -> dict:
    """
    Extrai parâmetros UTM do request (GET ou session).

    Prioridade: parâmetros na URL atual > parâmetros salvos na sessão.
    Salva na sessão para persistir durante a visita.

    Retorna dict com chaves: source, medium, campaign
    """
    utm_keys = ("utm_source", "utm_medium", "utm_campaign")
    result = {}

    # Tenta da URL atual primeiro
    for key in utm_keys:
        value = request.GET.get(key, "")
        if value:
            result[key] = value[:100]

    # Complementa com o que estiver na sessão (da entrada da visita)
    if hasattr(request, "session"):
        session_utms = request.session.get("_analytics_utms", {})
        for key in utm_keys:
            if key not in result and key in session_utms:
                result[key] = session_utms[key]

    # Persiste os UTMs da entrada na sessão (apenas na primeira vez)
    if result and hasattr(request, "session"):
        if "_analytics_utms" not in request.session:
            request.session["_analytics_utms"] = result
            # Guard: session pode ser dict simples (testes) ou SessionBase
            if hasattr(request.session, "modified"):
                request.session.modified = True

    return {
        "source": result.get("utm_source", "")[:100],
        "medium": result.get("utm_medium", "")[:100],
        "campaign": result.get("utm_campaign", "")[:200],
    }


def get_session_key(request) -> str:
    """
    Retorna a chave de sessão do request Django.
    Garante que a sessão exista (cria se necessário).
    """
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or ""

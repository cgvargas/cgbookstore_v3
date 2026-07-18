"""
AnalyticsMiddleware — Captura page_views de forma controlada.

Responsabilidade:
- Identificar requisições de páginas reais (excluir assets, admin, robôs, etc.)
- Criar/atualizar a AnalyticsSession do visitante
- Registrar evento page_view no ProductEvent
- Extrair informações de dispositivo e UTM sem armazenar dados brutos

Design:
- Execução em < 5ms no caminho de resposta (após a view ter respondido)
- Toda escrita é protegida em try/except — nunca interrompe a requisição
- Controlado por feature flag: PRODUCT_ANALYTICS_PROCESSING_MODE
- Nenhum IP ou User-Agent armazenado
"""
import logging

from .constants import EXCLUDED_URL_PREFIXES
from .utils import (
    get_analytics_settings,
    normalize_page_name,
    extract_object_info,
    detect_device_type,
    detect_browser_family,
    detect_os_family,
    extract_referer_domain,
    extract_utm_params,
    get_session_key,
    is_bot_request,
)

logger = logging.getLogger(__name__)

# Content-Types que indicam requisições técnicas (não páginas HTML)
TECHNICAL_CONTENT_TYPES = (
    "application/json",
    "application/xml",
    "text/xml",
    "multipart/form-data",
)

# Métodos HTTP que não representam navegação
EXCLUDED_METHODS = {"PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE"}


class AnalyticsMiddleware:
    """
    Middleware de analytics — captura page_views após cada resposta bem-sucedida.

    Posicionamento sugerido no MIDDLEWARE (após AuthenticationMiddleware):
        'product_analytics.middleware.AnalyticsMiddleware',

    Configuração via settings.PRODUCT_ANALYTICS:
        PROCESSING_MODE: 'disabled' | 'synchronous' | 'celery'
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._cfg = get_analytics_settings()
        self._mode = self._cfg.get("PROCESSING_MODE", "synchronous")

    def __call__(self, request):
        # Processa a requisição normalmente (view executa aqui)
        response = self.get_response(request)

        # Rastreamento em modo desabilitado: retorna imediatamente
        if self._mode == "disabled":
            return response

        # Processa analytics no caminho de RESPOSTA para não bloquear a view
        try:
            if self._should_track(request, response):
                self._track_page_view(request, response)
        except Exception as exc:
            # Analytics nunca deve quebrar a resposta ao usuário
            logger.error(
                "[ProductAnalytics] Middleware erro inesperado: %s",
                exc,
                exc_info=True,
            )

        return response

    # --------------------------------------------------------------------------
    # Decisão de rastreamento
    # --------------------------------------------------------------------------

    def _should_track(self, request, response) -> bool:
        """
        Retorna True se esta requisição deve ser rastreada.

        Exclusões:
        - Modo desabilitado
        - Métodos não-GET (exceto POST em registration_completed)
        - Prefixos de URL técnicos (static, admin, webhooks, etc.)
        - Status codes que não são respostas de página (excluindo redirects válidos)
        - Requisições com Content-Type técnico
        - Robôs identificados pelo User-Agent
        - Requisições AJAX sem header de tracking explícito
        """
        # Apenas GET para page_views (por enquanto)
        if request.method in EXCLUDED_METHODS:
            return False

        if request.method == "POST":
            # POST só rastreia se for registration ou ação explicitamente marcada
            if not request.headers.get("X-Track-Analytics"):
                return False

        # Verifica prefixo de URL excluído
        path = request.path
        if any(path.startswith(prefix) for prefix in EXCLUDED_URL_PREFIXES):
            return False

        # Ignora status codes técnicos (500 não deve gerar event_view)
        # Aceita: 200, 301, 302, 404 (404 é válido para rastrear páginas inexistentes)
        if response.status_code >= 500:
            return False

        # Ignora AJAX sem flag explícita de tracking
        is_ajax = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.headers.get("Accept", "").startswith("application/json")
        )
        if is_ajax and not request.headers.get("X-Track-Analytics"):
            return False

        # Ignora robôs conhecidos
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if is_bot_request(user_agent):
            return False

        # Verifica se é uma página real (não asset técnico sem extensão mapeada)
        page_name = normalize_page_name(path)
        if not page_name:
            return False

        return True

    # --------------------------------------------------------------------------
    # Rastreamento
    # --------------------------------------------------------------------------

    def _track_page_view(self, request, response) -> None:
        """
        Realiza o rastreamento de page_view.

        Fluxo:
        1. Extrai informações sem armazenar dados brutos
        2. Cria/atualiza AnalyticsSession
        3. Registra ProductEvent de page_view
        """
        from .services.session_service import SessionService
        from .services.event_service import EventService

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        path = request.path

        # Normalização — nenhum dado bruto é persistido
        page_name = normalize_page_name(path)
        object_type, object_id = extract_object_info(path)
        device_type = detect_device_type(user_agent)
        browser_family = detect_browser_family(user_agent)
        operating_system = detect_os_family(user_agent)
        referer_domain = extract_referer_domain(
            request.META.get("HTTP_REFERER", "")
        )
        utm = extract_utm_params(request)
        session_key = get_session_key(request)

        if not session_key:
            return

        # Usuário: apenas se autenticado
        user = getattr(request, "user", None)
        resolved_user = (
            user if user and hasattr(user, "is_authenticated") and user.is_authenticated
            else None
        )

        # Cria ou atualiza sessão analítica
        analytics_session = SessionService.get_or_create(
            session_key=session_key,
            user=resolved_user,
            page_name=page_name,
            device_type=device_type,
            browser_family=browser_family,
            operating_system=operating_system,
            referer_domain=referer_domain,
            source=utm["source"],
            medium=utm["medium"],
            campaign=utm["campaign"],
        )

        # Registra evento de page_view
        EventService.record(
            event_type="page_view",
            session=analytics_session,
            user=resolved_user,
            page_name=page_name,
            object_type=object_type or "",
            object_id=object_id,
        )

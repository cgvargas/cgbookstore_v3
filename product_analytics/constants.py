"""
Constantes do módulo Product Analytics.

Centraliza allowlists de eventos e chaves de metadata
para garantir consistência e evitar dados não-estruturados.
"""

# ==============================================================================
# ALLOWLIST DE TIPOS DE EVENTO (v1)
# ==============================================================================
# Adicionar novos tipos aqui conforme necessário — nunca aceitar strings livres.

ALLOWED_EVENT_TYPES = frozenset([
    # Navegação
    "page_view",

    # Busca
    "search_performed",

    # Funil de conversão Premium
    "premium_page_viewed",

    # Registro de usuário
    "registration_started",
    "registration_completed",

    # Ativação
    "first_meaningful_action",

    # Ciclo de sessão
    "session_started",
    "session_ended",
])

# ==============================================================================
# ALLOWLIST DE CHAVES DE METADATA
# ==============================================================================
# Somente estas chaves são persistidas no JSONField de metadata.
# Valores que não respeitem LGPD (IP, email, nome, senha) são rejeitados aqui.

ALLOWED_METADATA_KEYS = frozenset([
    "query_term_hash",    # SHA-256 truncado (16 hex chars) do termo de busca — sem o termo em si
    "result_count",       # int: quantidade de resultados retornados
    "search_type",        # str: 'title', 'author', 'category', 'isbn', 'full_text'
    "conversion_step",    # str: etapa no funil, ex: 'view_pricing', 'click_subscribe'
    "feature_name",       # str: nome da funcionalidade, ex: 'chatbot', 'library', 'ereader'
    "page_section",       # str: seção dentro da página, ex: 'hero', 'recommendations', 'reviews'
    "is_first_visit",     # bool: se é a primeira visita à page_name para este usuário
])

# ==============================================================================
# TIPOS DE OBJETO (object_type)
# ==============================================================================

ALLOWED_OBJECT_TYPES = frozenset([
    "book",
    "author",
    "category",
    "article",
    "event",
    "video",
    "quiz",
    "debate",
    "universe",
])

# ==============================================================================
# TIPOS DE DISPOSITIVO
# ==============================================================================

DEVICE_TYPE_DESKTOP = "desktop"
DEVICE_TYPE_MOBILE = "mobile"
DEVICE_TYPE_TABLET = "tablet"
DEVICE_TYPE_UNKNOWN = "unknown"

DEVICE_TYPE_CHOICES = [
    (DEVICE_TYPE_DESKTOP, "Desktop"),
    (DEVICE_TYPE_MOBILE, "Mobile"),
    (DEVICE_TYPE_TABLET, "Tablet"),
    (DEVICE_TYPE_UNKNOWN, "Desconhecido"),
]

# ==============================================================================
# MODOS DE PROCESSAMENTO
# ==============================================================================

PROCESSING_MODE_DISABLED = "disabled"
PROCESSING_MODE_SYNC = "synchronous"
PROCESSING_MODE_CELERY = "celery"

# ==============================================================================
# NOMES DE PÁGINAS NORMALIZADOS
# ==============================================================================
# Mapeamento de prefixos de URL para page_name canônico.
# A ordem importa: prefixos mais específicos primeiro.

URL_TO_PAGE_NAME = [
    # Exatas
    ("/", "home"),
    ("/sobre/", "about"),
    ("/contato/", "contact"),
    ("/faq/", "faq"),
    ("/privacidade/", "privacy"),
    ("/termos/", "terms"),
    ("/premium/", "premium_page"),
    ("/busca/", "search"),
    ("/busca", "search"),

    # Biblioteca pessoal
    ("/biblioteca/", "library"),
    ("/biblioteca", "library"),

    # Leitura
    ("/leitura/", "reading_progress"),
    ("/ereader/", "ereader"),

    # Conteúdo de livros
    ("/livros/", "book_detail"),
    ("/google-books/", "google_books"),

    # Autores
    ("/autores/", "author_detail"),

    # Gamificação
    ("/gamificacao/", "gamification"),
    ("/conquistas/", "achievements"),
    ("/ranking/", "ranking"),

    # Comunidade
    ("/debates/", "debates"),
    ("/noticias/", "news"),

    # Chatbot
    ("/chatbot/", "chatbot"),
    ("/assistente/", "chatbot"),

    # Universo literário
    ("/universo/", "literary_universe"),

    # Autenticação (allauth)
    ("/accounts/login/", "login"),
    ("/accounts/logout/", "logout"),
    ("/accounts/signup/", "registration"),
    ("/accounts/", "account_settings"),

    # Parceiros
    ("/parceiros/", "partners"),

    # Perfil
    ("/perfil/", "profile"),
    ("/dashboard/", "user_dashboard"),

    # Formulários e verificação
    ("/formulario/", "form_generator"),
    ("/verificacao/", "verification"),
]

# ==============================================================================
# EXCLUSÕES DO MIDDLEWARE
# ==============================================================================

# Prefixos de URL que nunca devem ser rastreados
EXCLUDED_URL_PREFIXES = (
    "/static/",
    "/media/",
    "/favicon.ico",
    "/favicon",
    "/admin/",
    "/webhooks/",
    "/api/internal/",
    "/health/",
    "/ping/",
    "/readiness/",
    "/liveness/",
    "/__debug__/",       # Django Debug Toolbar
    "/silk/",            # Django Silk profiler
)

# User-Agents de robôs conhecidos (lowercase substring match)
BOT_USER_AGENT_SUBSTRINGS = (
    "googlebot",
    "bingbot",
    "slurp",             # Yahoo
    "duckduckbot",
    "baiduspider",
    "yandexbot",
    "facebot",
    "ia_archiver",
    "semrushbot",
    "ahrefsbot",
    "dotbot",
    "petalbot",
    "seznambot",
    "mj12bot",
    "uptimerobot",
    "pingdom",
    "datadog",
    "python-requests",
    "python-httpx",
    "go-http-client",
    "java/",
    "curl/",
    "wget/",
    "scrapy",
    "lighthouse",        # Chrome Lighthouse
)

# ==============================================================================
# MÉTRICAS DE SNAPSHOT
# ==============================================================================

METRIC_DAU = "dau"
METRIC_WAU = "wau"
METRIC_MAU = "mau"
METRIC_DAU_MAU_RATIO = "dau_mau_ratio"
METRIC_RETENTION_D1 = "retention_d1"
METRIC_RETENTION_D7 = "retention_d7"
METRIC_RETENTION_D30 = "retention_d30"
METRIC_NEW_USERS = "new_users"
METRIC_PREMIUM_CONVERSIONS = "premium_conversions"
METRIC_SESSIONS_TOTAL = "sessions_total"
METRIC_PAGE_VIEWS_TOTAL = "page_views_total"
METRIC_SEARCHES_TOTAL = "searches_total"
METRIC_PARTNER_CLICKS = "partner_clicks"
METRIC_CHATBOT_SESSIONS = "chatbot_sessions"
METRIC_BOOKS_ADDED = "books_added"
METRIC_BOOKS_COMPLETED = "books_completed"
METRIC_AVG_SESSION_DURATION_SECONDS = "avg_session_duration_seconds"
METRIC_PAGES_PER_SESSION = "pages_per_session"

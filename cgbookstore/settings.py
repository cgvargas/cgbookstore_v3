import logging
import dj_database_url
from decouple import config
import os
from pathlib import Path

# Supabase Configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY', default='')
SUPABASE_SERVICE_KEY = config('SUPABASE_SERVICE_KEY', default='')

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-9eojq)3m)cznln$43_3%1lh5ofx4qjh+!7+%51f5m+2(t@_swe')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# CSRF Trusted Origins para produção
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000'
).split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Requerido pelo allauth

    # Django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Providers sociais (sem GitHub)
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    # Meus Apps
    'core.apps.CoreConfig',
    'chatbot_literario.apps.ChatbotLiterarioConfig',
    'accounts.apps.AccountsConfig',
    'debates',
    'recommendations',
    'finance.apps.FinanceConfig',

    # Third-party Apps
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve arquivos estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Requerido pelo allauth
    'core.middleware.RateLimitMiddleware',  # Rate limiting
]

ROOT_URLCONF = 'cgbookstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cgbookstore.wsgi.application'


# Database
# Usar DATABASE_URL do ambiente, ou fallback para SQLite local em desenvolvimento
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3')),
        conn_max_age=600,  # 10 minutos (aumentado de 60s para melhor pooling)
        conn_health_checks=True,
    )
}

# Adicionar opções de timeout ao banco de dados (apenas para PostgreSQL)
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000'  # 30s timeout para queries
    }


# ==============================================================================
# CACHE CONFIGURATION (Redis)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,  # Fallback se Redis cair
        },
        'KEY_PREFIX': 'cgbookstore',
        'TIMEOUT': config('REDIS_CACHE_TIMEOUT', default=300, cast=int),
    }
}

# Cache de sessões (reduz carga no banco)
# TEMPORARIAMENTE DESABILITADO - Usar sessões em banco até resolver Redis
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'

# Sessões em banco de dados (padrão Django)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# CELERY CONFIGURATION
# ==============================================================================

CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos
CELERY_RESULT_EXPIRES = 3600  # 1 hora


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# ==============================================================================
# CONFIGURAÇÃO DE MÍDIA E ARMAZENAMENTO
# ==============================================================================

# Armazenamento local (fallback)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Controle de uso do Supabase Storage
USE_SUPABASE_STORAGE = config('USE_SUPABASE_STORAGE', default=True, cast=bool)

# Configuração de Storage Backends (Django 4.2+)
if USE_SUPABASE_STORAGE and SUPABASE_URL and SUPABASE_ANON_KEY:
    # Usar Supabase Storage para uploads
    STORAGES = {
        "default": {
            "BACKEND": "core.storage_backends.SupabaseMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    logger.info("✅ Usando Supabase Storage para arquivos de mídia")
else:
    # Usar armazenamento local
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    logger.info("⚠️ Usando armazenamento local para arquivos de mídia")


# Google Books API Configuration
GOOGLE_BOOKS_API_KEY = config('GOOGLE_BOOKS_API_KEY', default='')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redireciona para a home page após o login
LOGIN_REDIRECT_URL = '/'

# Redireciona para a home page após o logout (opcional, já que a LogoutView pode fazer isso)
LOGOUT_REDIRECT_URL = '/'


# ========== SISTEMA DE RECOMENDAÇÕES IA ==========

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # Permite login via sessão Django
        'rest_framework.authentication.BasicAuthentication',
    ],
    # Removido DEFAULT_PERMISSION_CLASSES para permitir acesso via sessão
    # Cada view controla suas próprias permissões
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Google Gemini AI
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

# ==============================================================================
# MERCADO PAGO - MÓDULO FINANCEIRO
# ==============================================================================
MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN', default='')
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY', default='')
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Email Configuration
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@cgbookstore.com')

# Determinar backend de email baseado no ambiente
if config('USE_BREVO_API', default=False, cast=bool):
    # Usar Brevo API (recomendado para produção)
    EMAIL_BACKEND = 'cgbookstore.backends.brevo.BrevoBackend'
    BREVO_API_KEY = config('EMAIL_HOST_PASSWORD', default='')  # Reutilizar mesma env var
elif config('USE_SENDGRID_API', default=False, cast=bool):
    # Usar SendGrid Web API (alternativa)
    EMAIL_BACKEND = 'cgbookstore.backends.sendgrid.SendGridBackend'
    SENDGRID_API_KEY = config('EMAIL_HOST_PASSWORD', default='')
else:
    # Usar backend padrão (console ou SMTP)
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

    # SMTP Configuration (usado em produção se não usar APIs)
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Configurações de Recomendações
RECOMMENDATIONS_CONFIG = {
    'MIN_INTERACTIONS': 5,  # Mínimo de interações para gerar recomendações personalizadas
    'CACHE_TIMEOUT': 3600,  # Cache de 1 hora para recomendações
    'SIMILARITY_CACHE_TIMEOUT': 86400,  # Cache de 24 horas para similaridade
    'MAX_RECOMMENDATIONS': 10,  # Número máximo de recomendações retornadas
    'HYBRID_WEIGHTS': {
        'collaborative': 0.6,  # Peso da filtragem colaborativa
        'content': 0.3,        # Peso da filtragem baseada em conteúdo
        'trending': 0.1,       # Peso dos livros em alta
    },
}

# ==============================================================================
# DJANGO-ALLAUTH CONFIGURATION
# ==============================================================================

# Site ID (requerido pelo allauth)
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    # Backend nativo do Django (username + password)
    'django.contrib.auth.backends.ModelBackend',
    # Backend do allauth (email + password, social)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ===== NOVO FORMATO (Django-allauth 0.57+) =====
# Métodos de login permitidos: email e username
ACCOUNT_LOGIN_METHODS = {'email', 'username'}

# Campos obrigatórios no cadastro
# email* = obrigatório, username* = obrigatório, password1* e password2* = senhas
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Verificação de email: 'optional', 'mandatory', ou 'none'
# 'mandatory' = bloqueia login até verificar email (muito restritivo)
# 'optional' = pede verificação no cadastro, mas permite login (RECOMENDADO)
# 'none' = não pede verificação
# Usando 'optional' para melhor UX - novos usuários recebem email mas usuários
# existentes podem fazer login normalmente
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Email é obrigatório no cadastro
ACCOUNT_EMAIL_REQUIRED = True

# Impedir que usuários logados acessem páginas de signup/login
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

# Não pedir confirmação de email novamente para usuários já autenticados
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_REDIRECT_URL

# Permitir usuários registrarem-se
ACCOUNT_SIGNUP_ENABLED = True

# Não permitir emails duplicados
ACCOUNT_UNIQUE_EMAIL = True

# Prevenir enumeração de usuários via email
# False = mostra erro claro "email já existe" na página de cadastro
# True = não revela se email existe (envia email em ambos os casos por segurança)
# Configurando False para melhor UX - usuário vê erro imediato na tela
ACCOUNT_PREVENT_ENUMERATION = False

# Mensagem de confirmação de email
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Link expira em 3 dias
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[CGBookStore] '

# Redirecionamento após login (já existe, mas allauth usa)
LOGIN_URL = '/accounts/login/'
ACCOUNT_LOGIN_URL = '/accounts/login/'

# Confirmar logout (False = logout direto sem confirmação)
ACCOUNT_LOGOUT_ON_GET = False

# Auto-signup com social account (sem confirmação extra)
SOCIALACCOUNT_AUTO_SIGNUP = True

# Perguntar email se provider não fornecer
SOCIALACCOUNT_QUERY_EMAIL = True

# Conectar accounts existentes por email
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Configuração dos providers sociais (Google e Facebook)
# Credenciais serão carregadas do .env
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID', default='')
FACEBOOK_APP_SECRET = config('FACEBOOK_APP_SECRET', default='')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        # APP configuration removed - use database SocialApp instead
        # 'APP': {
        #     'client_id': GOOGLE_CLIENT_ID,
        #     'secret': GOOGLE_CLIENT_SECRET,
        #     'key': ''
        # }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v18.0',
        # APP configuration removed - use database SocialApp instead
        # 'APP': {
        #     'client_id': FACEBOOK_APP_ID,
        #     'secret': FACEBOOK_APP_SECRET,
        #     'key': ''
        # }
    }
}

# Adapters customizados
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ==============================================================================

if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Outras configurações de segurança
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # WhiteNoise para arquivos estáticos
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}


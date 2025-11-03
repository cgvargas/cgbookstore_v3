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
SECRET_KEY = 'django-insecure-9eojq)3m)cznln$43_3%1lh5ofx4qjh+!7+%51f5m+2(t@_swe'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,  # 10 minutos (aumentado de 60s para melhor pooling)
        conn_health_checks=True,
    )
}

# Adicionar opções de timeout ao banco de dados
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
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

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


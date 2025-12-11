"""
Configurações específicas para executar testes locais com SQLite.
Use: python manage.py test --settings=cgbookstore.settings_test
"""
from .settings import *

# Força SQLite para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Desabilita Supabase Storage para testes
USE_SUPABASE_STORAGE = False

# Desabilita cache Redis (usa cache local em memória)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Desabilita envio de emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Acelera testes de senha
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Exclui apps com migrações incompatíveis com SQLite
# Esses apps podem ser testados diretamente no PostgreSQL
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in (
    'new_authors.apps.NewAuthorsConfig',
    'new_authors',
)]

# Silencia logs durante testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

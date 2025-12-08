#!/usr/bin/env bash
# exit on error
set -o errexit

echo '🚀 Starting optimized build process...'

# Install dependencies
echo '📦 Installing dependencies...'
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo '📁 Collecting static files...'
python manage.py collectstatic --no-input

# ❌ REMOVED: makemigrations (deve ser feito LOCALMENTE, não no build!)
# Migrations devem estar commitadas no repositório

# Run migrations (sem verbose para ser mais rápido)
echo '🗄️ Running database migrations...'
python manage.py migrate --no-input

# ❌ REMOVED: showmigrations (apenas debug, desnecessário em produção)

# ❌ REMOVED: cleanup_socialapps (executar apenas quando necessário)

# Setup initial data (silencioso, falha não é crítica)
echo '⚙️ Setting up initial data...'
python manage.py setup_initial_data --skip-superuser --skip-social 2>/dev/null || echo 'ℹ️ Initial data already exists'

# Create superuser if environment variable is set
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo '👤 Creating superuser...'
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
import os;
User = get_user_model();
username = os.getenv('SUPERUSER_USERNAME', 'admin');
email = os.getenv('SUPERUSER_EMAIL', 'admin@cgbookstore.com');
password = os.getenv('SUPERUSER_PASSWORD', 'admin123');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print(f'✅ Superuser criado: {username}');
else:
    print(f'ℹ️ Superuser já existe');
" 2>/dev/null || true
fi

echo '✅ Build completed successfully!'

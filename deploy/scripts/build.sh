#!/usr/bin/env bash
# exit on error
set -o errexit

echo 'Starting build process...'

# Install dependencies
echo 'Installing dependencies...'
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo 'Collecting static files...'
python manage.py collectstatic --no-input

# Create migrations
echo 'Checking for new migrations...'
python manage.py makemigrations --no-input

# Run migrations with verbose output
echo 'Running database migrations...'
python manage.py migrate --no-input --verbosity 2

# Verify migrations
echo 'Verifying database setup...'
python manage.py showmigrations

# Setup initial data (Site, Categories, Sample Books, Social Apps)
echo 'Setting up initial data...'
python manage.py setup_initial_data --skip-superuser || echo 'Initial data setup completed with warnings'

# Fix duplicate SocialApps and other database issues
echo 'Fixing database duplicates...'
python manage.py fix_duplicates || echo 'Database fixes completed with warnings'

# Create superuser if environment variable is set
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo 'Creating superuser from environment variables...'
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
import os;
User = get_user_model();
username = os.getenv('SUPERUSER_USERNAME', 'admin');
email = os.getenv('SUPERUSER_EMAIL', 'admin@cgbookstore.com');
password = os.getenv('SUPERUSER_PASSWORD', 'admin123');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print(f'✅ Superuser created: {username} / {email}');
    print('⚠️  IMPORTANTE: Altere a senha após primeiro login!');
else:
    print(f'⚠️  Superuser {username} already exists');
" || echo "Superuser creation skipped"
fi

echo 'Build completed successfully!'

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

echo 'Build completed successfully!'

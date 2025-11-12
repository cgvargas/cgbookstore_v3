# Generated migration for Google OAuth setup

from django.db import migrations
from decouple import config


def setup_google_oauth(apps, schema_editor):
    """
    Automatically creates Google SocialApp from environment variables.
    Runs during migration (safe for Render deploy without Shell access).
    """
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    # Get credentials from environment
    client_id = config('GOOGLE_CLIENT_ID', default='')
    client_secret = config('GOOGLE_CLIENT_SECRET', default='')

    # Skip if credentials not configured
    if not client_id or not client_secret:
        print('⚠️  Google OAuth credentials not found in environment. Skipping setup.')
        return

    # Get Site (usually ID=1)
    try:
        site = Site.objects.get(id=1)
    except Site.DoesNotExist:
        print('⚠️  Site with ID=1 not found. Skipping Google OAuth setup.')
        return

    # Delete existing Google apps (prevent duplicates)
    deleted_count = SocialApp.objects.filter(provider='google').delete()[0]
    if deleted_count > 0:
        print(f'🗑️  Deleted {deleted_count} existing Google SocialApp(s)')

    # Create new Google SocialApp
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google',
        client_id=client_id,
        secret=client_secret,
    )
    google_app.sites.add(site)

    print(f'✅ Google OAuth configured successfully!')
    print(f'   - Provider: google')
    print(f'   - Client ID: {client_id[:20]}...')
    print(f'   - Site: {site.domain}')


def reverse_setup(apps, schema_editor):
    """Remove Google SocialApp if rolling back"""
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()
    print('🔄 Google OAuth SocialApp removed (migration rollback)')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
        ('sites', '0001_initial'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
    ]

    operations = [
        migrations.RunPython(setup_google_oauth, reverse_setup),
    ]

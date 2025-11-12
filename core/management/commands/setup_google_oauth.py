"""
Management command to setup Google OAuth SocialApp
Run: python manage.py setup_google_oauth
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Setup Google OAuth SocialApp from environment variables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Starting Google OAuth Setup...\n'))

        # Get credentials from environment
        client_id = config('GOOGLE_CLIENT_ID', default='')
        client_secret = config('GOOGLE_CLIENT_SECRET', default='')

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR(
                '❌ ERROR: Google credentials not found in environment variables!\n'
                'Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET'
            ))
            return

        # Get current site
        try:
            site = Site.objects.get(id=1)
            self.stdout.write(self.style.SUCCESS(f'✓ Site found: {site.domain}'))
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ ERROR: Site with ID=1 not found!'))
            return

        # Check for existing Google apps
        existing_apps = SocialApp.objects.filter(provider='google')

        if existing_apps.exists():
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  Found {existing_apps.count()} existing Google SocialApp(s):'
            ))
            for app in existing_apps:
                self.stdout.write(f'   - ID: {app.id}, Name: {app.name}')

            # Ask to delete (auto-confirm in non-interactive mode)
            self.stdout.write(self.style.WARNING('\n🗑️  Deleting existing Google apps...'))
            count = existing_apps.count()
            existing_apps.delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {count} old Google app(s)'))

        # Create new Google SocialApp
        self.stdout.write(self.style.WARNING('\n📝 Creating new Google SocialApp...'))

        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret,
        )
        google_app.sites.add(site)

        self.stdout.write(self.style.SUCCESS(
            f'✓ Google SocialApp created successfully!\n'
            f'  - Provider: {google_app.provider}\n'
            f'  - Name: {google_app.name}\n'
            f'  - Client ID: {client_id[:20]}...\n'
            f'  - Site: {site.domain}\n'
        ))

        # Verify final state
        total_apps = SocialApp.objects.filter(provider='google').count()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ SETUP COMPLETE!\n'
            f'Total Google SocialApps in database: {total_apps}\n\n'
            f'Next steps:\n'
            f'1. Verify Google OAuth is configured in Google Cloud Console\n'
            f'2. Ensure redirect URI is: https://your-domain.com/accounts/google/login/callback/\n'
            f'3. Test login at: /accounts/login/\n'
        ))

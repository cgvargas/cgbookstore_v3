"""
Comando para fazer limpeza FORÇADA de SocialApps duplicados.
Uso: python manage.py cleanup_socialapps
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'FORCA limpeza total e recriacao de SocialApps'

    def handle(self, *args, **options):
        self.stdout.write("="*70)
        self.stdout.write("LIMPEZA FORCADA DE SOCIALAPPS")
        self.stdout.write("="*70)

        with transaction.atomic():
            # 1. DELETAR TODOS os SocialApps sem exceção
            total_antes = SocialApp.objects.all().count()
            self.stdout.write(f"\nTotal de SocialApps ANTES: {total_antes}")

            if total_antes > 0:
                # Listar todos antes de deletar
                self.stdout.write("\nSocialApps encontrados:")
                for app in SocialApp.objects.all():
                    self.stdout.write(f"   ID {app.id}: {app.provider} - {app.name}")

                # DELETAR TUDO
                SocialApp.objects.all().delete()
                self.stdout.write(self.style.WARNING(f"\n  {total_antes} SocialApps DELETADOS"))

            # 2. Verificar que está vazio
            count_after_delete = SocialApp.objects.all().count()
            if count_after_delete > 0:
                self.stdout.write(self.style.ERROR(f"\nERRO: Ainda existem {count_after_delete} SocialApps apos delecao!"))
                return
            else:
                self.stdout.write(self.style.SUCCESS("\n  Banco zerado com sucesso"))

            # 3. Recriar SocialApps do zero
            self.stdout.write("\nRecriando SocialApps...")

            google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
            google_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
            facebook_app_id = os.getenv('FACEBOOK_APP_ID', '')
            facebook_secret = os.getenv('FACEBOOK_APP_SECRET', '')

            site = Site.objects.get(id=1)
            created_apps = []

            # Google
            if google_client_id and google_secret:
                self.stdout.write("\n  Criando Google OAuth...")
                google_app = SocialApp(
                    provider='google',
                    name='Google',
                    client_id=google_client_id,
                    secret=google_secret,
                )
                google_app.save()
                google_app.sites.add(site)
                created_apps.append(f"Google (ID {google_app.id})")
                self.stdout.write(self.style.SUCCESS(f"    OK: Google OAuth criado (ID: {google_app.id})"))

            # Facebook
            if facebook_app_id and facebook_secret:
                self.stdout.write("\n  Criando Facebook OAuth...")
                facebook_app = SocialApp(
                    provider='facebook',
                    name='Facebook',
                    client_id=facebook_app_id,
                    secret=facebook_secret,
                )
                facebook_app.save()
                facebook_app.sites.add(site)
                created_apps.append(f"Facebook (ID {facebook_app.id})")
                self.stdout.write(self.style.SUCCESS(f"    OK: Facebook OAuth criado (ID: {facebook_app.id})"))

            # 4. Verificação final
            self.stdout.write("\n" + "="*70)
            self.stdout.write("VERIFICACAO FINAL")
            self.stdout.write("="*70)

            final_count = SocialApp.objects.all().count()
            self.stdout.write(f"\nTotal de SocialApps: {final_count}")

            for app in SocialApp.objects.all():
                sites_count = app.sites.count()
                self.stdout.write(f"  ID {app.id}: {app.provider} ({app.name}) - {sites_count} sites")

            # Verificar duplicatas
            from django.db.models import Count
            duplicates = SocialApp.objects.values('provider').annotate(
                count=Count('id')
            ).filter(count__gt=1)

            if duplicates.exists():
                self.stdout.write(self.style.ERROR(f"\nERRO: Ainda existem duplicatas!"))
                for dup in duplicates:
                    self.stdout.write(self.style.ERROR(f"   Provider '{dup['provider']}': {dup['count']} apps"))
            else:
                self.stdout.write(self.style.SUCCESS("\n  Nenhuma duplicata encontrada!"))

            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("LIMPEZA CONCLUIDA COM SUCESSO!"))
            self.stdout.write("="*70)

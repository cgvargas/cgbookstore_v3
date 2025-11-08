"""
Management command para corrigir duplicatas de SocialApp e outros problemas.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Corrige SocialApps duplicados e outros problemas do banco'

    def handle(self, *args, **options):
        self.stdout.write("="*70)
        self.stdout.write("Corrigindo duplicatas...")
        self.stdout.write("="*70)

        # Corrigir SocialApps duplicados
        self.fix_duplicate_socialapps()

        self.stdout.write("="*70)
        self.stdout.write(self.style.SUCCESS("Correcoes concluidas!"))
        self.stdout.write("="*70)

    def fix_duplicate_socialapps(self):
        """Remove SocialApps duplicados, mantendo apenas o mais antigo."""
        self.stdout.write("\nVerificando SocialApps duplicados...")

        # Verificar duplicatas por provider
        duplicates = SocialApp.objects.values('provider').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        if not duplicates.exists():
            self.stdout.write(self.style.SUCCESS("  Nenhum SocialApp duplicado encontrado"))
            return

        self.stdout.write(self.style.WARNING(f"  Encontrados {duplicates.count()} providers duplicados"))

        for dup in duplicates:
            provider = dup['provider']
            count = dup['count']

            self.stdout.write(f"\n  Provider '{provider}': {count} apps")

            # Pegar todos os apps desse provider, ordenados por ID (mais antigo primeiro)
            apps = SocialApp.objects.filter(provider=provider).order_by('id')

            # Mostrar info
            for app in apps:
                self.stdout.write(f"    - ID {app.id}, sites: {app.sites.count()}")

            # Manter apenas o PRIMEIRO (mais antigo)
            apps_to_delete = list(apps[1:])  # Todos exceto o primeiro

            if apps_to_delete:
                self.stdout.write(self.style.WARNING(
                    f"  Deletando {len(apps_to_delete)} apps duplicados de '{provider}'..."
                ))

                for app in apps_to_delete:
                    self.stdout.write(f"     Deletando ID {app.id}")
                    app.delete()

                self.stdout.write(self.style.SUCCESS(f"  {len(apps_to_delete)} duplicatas removidas de '{provider}'"))

        # Verificar estado final
        final_count = SocialApp.objects.values('provider').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()

        if final_count == 0:
            self.stdout.write(self.style.SUCCESS("\n  Todas as duplicatas foram removidas!"))
        else:
            self.stdout.write(self.style.ERROR(f"\n  Ainda existem {final_count} duplicatas!"))

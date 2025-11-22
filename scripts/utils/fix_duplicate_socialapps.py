"""
Script para remover SocialApps duplicados.
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("Verificando SocialApps duplicados...")

# Listar todos os SocialApps
all_apps = SocialApp.objects.all()
print(f"\nTotal de SocialApps: {all_apps.count()}")

for app in all_apps:
    print(f"  - ID {app.id}: {app.provider} (client_id: {app.client_id[:20]}...)")

# Verificar duplicatas por provider
from django.db.models import Count
duplicates = SocialApp.objects.values('provider').annotate(count=Count('id')).filter(count__gt=1)

if duplicates.exists():
    print(f"\n⚠️  Encontrados {duplicates.count()} providers duplicados:")

    for dup in duplicates:
        provider = dup['provider']
        count = dup['count']
        print(f"\n  Provider '{provider}': {count} apps")

        apps = SocialApp.objects.filter(provider=provider).order_by('id')

        for app in apps:
            print(f"    - ID {app.id}, criado em: {app.id} (sites: {app.sites.count()})")

        # Manter apenas o PRIMEIRO (mais antigo)
        apps_to_delete = apps[1:]  # Todos exceto o primeiro

        if apps_to_delete:
            print(f"  🗑️  Deletando {len(apps_to_delete)} apps duplicados de '{provider}'...")
            for app in apps_to_delete:
                print(f"     Deletando ID {app.id}")
                app.delete()

    print("\n✅ Duplicatas removidas!")
else:
    print("\n✅ Nenhum provider duplicado encontrado!")

# Verificar estado final
print(f"\n📊 Estado final:")
final_apps = SocialApp.objects.all()
print(f"  Total de SocialApps: {final_apps.count()}")
for app in final_apps:
    print(f"    - {app.provider}: {app.sites.count()} sites configurados")

"""
Script para atualizar UserProfiles com dados do Supabase.
"""
import django
import os
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import UserProfile
from core.models import Category

# Carregar dados do backup
print("Carregando dados do UserProfile do Supabase...")
with open('temp_accounts_userprofile.json', 'r', encoding='utf-8') as f:
    profiles_data = json.load(f)

print(f"Total de profiles no backup: {len(profiles_data)}")

# Atualizar cada profile
updated = 0
created = 0
errors = 0

for item in profiles_data:
    user_id = item['fields']['user']
    fields = item['fields'].copy()
    del fields['user']  # Remover o campo user (já é a FK)

    # Converter favorite_genre de ID para instância
    if 'favorite_genre' in fields and fields['favorite_genre']:
        try:
            category_id = fields['favorite_genre']
            fields['favorite_genre_id'] = category_id  # Usar _id para atribuição direta
            del fields['favorite_genre']
        except:
            del fields['favorite_genre']  # Remover se der erro

    try:
        # Buscar ou criar profile
        profile, was_created = UserProfile.objects.update_or_create(
            user_id=user_id,
            defaults=fields
        )

        if was_created:
            print(f"✅ Criado: User ID {user_id}")
            created += 1
        else:
            print(f"✅ Atualizado: User ID {user_id}")
            updated += 1

    except Exception as e:
        print(f"❌ Erro no User ID {user_id}: {e}")
        errors += 1

print(f"\n{'='*70}")
print(f"📊 RESUMO:")
print(f"   Profiles atualizados: {updated}")
print(f"   Profiles criados: {created}")
print(f"   Erros: {errors}")
print(f"{'='*70}")

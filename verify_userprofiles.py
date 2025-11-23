"""
Script para verificar integridade de UserProfiles.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.db.models import Count

print('=' * 70)
print('📊 VERIFICAÇÃO COMPLETA DE USERPROFILES')
print('=' * 70)

# Estatísticas gerais
total_users = User.objects.count()
total_profiles = UserProfile.objects.count()

print(f'\n📈 Estatísticas:')
print(f'   Total de Users: {total_users}')
print(f'   Total de UserProfiles: {total_profiles}')
print(f'   Diferença: {abs(total_users - total_profiles)}')

if total_users == total_profiles:
    print('   ✅ Quantidade OK (1 perfil por usuário)')
else:
    print(f'   ⚠️ Há diferença de {abs(total_users - total_profiles)} perfis!')

# Verificar duplicatas
print(f'\n🔍 Verificando duplicatas...')
duplicates = UserProfile.objects.values('user_id').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print(f'   ⚠️ Encontradas {duplicates.count()} duplicatas!')
    for dup in duplicates:
        user = User.objects.get(id=dup['user_id'])
        print(f'   - User ID: {user.id}, Username: {user.username}, Profiles: {dup["count"]}')
else:
    print('   ✅ Nenhuma duplicata encontrada')

# Verificar usuários sem profile
users_without_profile = User.objects.filter(userprofile__isnull=True)
if users_without_profile.exists():
    print(f'\n⚠️ {users_without_profile.count()} usuários SEM perfil:')
    for u in users_without_profile[:10]:
        print(f'   - ID: {u.id}, Username: {u.username}, Email: {u.email}')
else:
    print(f'\n✅ Todos os usuários têm perfil')

# Mostrar últimos usuários criados
print(f'\n📋 Últimos 5 usuários criados:')
recent_users = User.objects.order_by('-date_joined')[:5]
for u in recent_users:
    has_profile = hasattr(u, 'profile') and u.profile is not None
    profile_status = '✅' if has_profile else '❌'
    print(f'   {profile_status} ID: {u.id}, Username: {u.username}, Criado: {u.date_joined.strftime("%Y-%m-%d %H:%M")}')

print(f'\n✅ Verificação concluída!')

"""
Script para diagnosticar e corrigir problema de UserProfile duplicado.

PROBLEMA: IntegrityError - duplicate key value violates unique constraint "accounts_userprofile_user_id_key"
CAUSA: Usuário existe mas UserProfile duplicado ou signal criando profile automaticamente

Execute: python fix_userprofile_duplicate.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.db import transaction


def diagnosticar():
    """Diagnostica o problema do User id=26."""
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DO PROBLEMA DE USERPROFILE")
    print("=" * 70)

    # 1. Verificar User id=26
    print("\n1️⃣ Verificando User id=26...")
    try:
        user = User.objects.get(id=26)
        print(f"   ✓ User encontrado:")
        print(f"     - Username: {user.username}")
        print(f"     - Email: {user.email}")
        print(f"     - is_active: {user.is_active}")
        print(f"     - is_staff: {user.is_staff}")
        print(f"     - is_superuser: {user.is_superuser}")
        print(f"     - Data criação: {user.date_joined}")
    except User.DoesNotExist:
        print("   ✗ User id=26 NÃO existe no banco")
        return None

    # 2. Verificar UserProfile
    print("\n2️⃣ Verificando UserProfile para user_id=26...")
    profiles = UserProfile.objects.filter(user_id=26)
    count = profiles.count()

    if count == 0:
        print("   ✗ NENHUM UserProfile encontrado (deveria ter 1)")
    elif count == 1:
        print(f"   ✓ 1 UserProfile encontrado (correto)")
        profile = profiles.first()
        print(f"     - ID: {profile.id}")
        print(f"     - Bio: {profile.bio[:50] if profile.bio else 'Vazia'}...")
    else:
        print(f"   ⚠️  {count} UserProfiles encontrados (DUPLICADOS!)")
        for i, profile in enumerate(profiles, 1):
            print(f"     #{i} - ID: {profile.id}, Criado: {profile.user.date_joined}")

    # 3. Verificar usuários sem perfil
    print("\n3️⃣ Verificando usuários sem UserProfile...")
    users_without_profile = User.objects.filter(profile__isnull=True)
    count = users_without_profile.count()

    if count > 0:
        print(f"   ⚠️  {count} usuários SEM perfil:")
        for u in users_without_profile[:10]:
            print(f"     - ID: {u.id}, Username: {u.username}, Email: {u.email}")
    else:
        print("   ✓ Todos os usuários têm perfil")

    # 4. Verificar todos os usuários
    print("\n4️⃣ Resumo geral...")
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    print(f"   📊 Total de Users: {total_users}")
    print(f"   📊 Total de UserProfiles: {total_profiles}")

    if total_users == total_profiles:
        print("   ✓ Quantidade correta (1 perfil por usuário)")
    else:
        print(f"   ⚠️  Diferença: {abs(total_users - total_profiles)} perfis a mais/menos")

    return user


def corrigir_user_26():
    """Corrige o problema específico do User id=26."""
    print("\n" + "=" * 70)
    print("🔧 CORREÇÃO DO PROBLEMA")
    print("=" * 70)

    try:
        user = User.objects.get(id=26)
    except User.DoesNotExist:
        print("\n✗ User id=26 não existe. Nada a corrigir.")
        return False

    profiles = UserProfile.objects.filter(user_id=26)
    count = profiles.count()

    if count == 0:
        print(f"\n1️⃣ User id=26 ({user.username}) não tem perfil. Criando...")
        try:
            with transaction.atomic():
                profile = UserProfile.objects.create(
                    user=user,
                    bio='',
                    favorite_genres=[]
                )
                print(f"   ✓ UserProfile criado com sucesso! ID: {profile.id}")
                return True
        except Exception as e:
            print(f"   ✗ Erro ao criar perfil: {e}")
            return False

    elif count == 1:
        print(f"\n✓ User id=26 ({user.username}) já tem 1 perfil. Nada a corrigir.")
        return True

    else:
        print(f"\n⚠️  User id=26 ({user.username}) tem {count} perfis DUPLICADOS!")
        print("   Mantendo o primeiro perfil e removendo duplicatas...")

        try:
            with transaction.atomic():
                # Manter o primeiro (mais antigo)
                first_profile = profiles.order_by('id').first()
                duplicates = profiles.exclude(id=first_profile.id)

                print(f"   📌 Mantendo perfil ID: {first_profile.id}")

                for dup in duplicates:
                    print(f"   🗑️  Removendo duplicata ID: {dup.id}")
                    dup.delete()

                print(f"   ✓ {count - 1} perfis duplicados removidos com sucesso!")
                return True
        except Exception as e:
            print(f"   ✗ Erro ao remover duplicatas: {e}")
            return False


def criar_perfis_faltantes():
    """Cria perfis para usuários que não têm."""
    print("\n" + "=" * 70)
    print("🔧 CRIANDO PERFIS FALTANTES")
    print("=" * 70)

    users_without_profile = User.objects.filter(profile__isnull=True)
    count = users_without_profile.count()

    if count == 0:
        print("\n✓ Todos os usuários já têm perfil!")
        return True

    print(f"\n📋 Encontrados {count} usuários sem perfil. Criando...")

    created = 0
    errors = 0

    for user in users_without_profile:
        try:
            with transaction.atomic():
                UserProfile.objects.create(
                    user=user,
                    bio='',
                    favorite_genres=[]
                )
                print(f"   ✓ Perfil criado para: {user.username} (ID: {user.id})")
                created += 1
        except Exception as e:
            print(f"   ✗ Erro ao criar perfil para {user.username}: {e}")
            errors += 1

    print(f"\n📊 Resultado:")
    print(f"   - Perfis criados: {created}")
    print(f"   - Erros: {errors}")

    return errors == 0


def verificar_signals():
    """Verifica se há signals configurados para UserProfile."""
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO SIGNALS")
    print("=" * 70)

    print("\n📝 Procurando signals em accounts/signals.py...")

    import os
    signals_file = 'accounts/signals.py'

    if os.path.exists(signals_file):
        print(f"   ✓ Arquivo encontrado: {signals_file}")
        print("\n   Conteúdo:")
        with open(signals_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Mostrar linhas relevantes
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'post_save' in line.lower() or 'UserProfile' in line:
                    print(f"     Linha {i}: {line}")
    else:
        print(f"   ℹ️  Arquivo não encontrado: {signals_file}")
        print("   Signals podem estar em outro lugar ou não existir")


def main():
    """Função principal."""
    print("\n🚀 Iniciando diagnóstico e correção...\n")

    # 1. Diagnosticar
    user = diagnosticar()

    if user is None:
        print("\n❌ Não foi possível continuar. User id=26 não existe.")
        return

    # 2. Perguntar se quer corrigir
    print("\n" + "=" * 70)
    resposta = input("\n❓ Deseja corrigir os problemas encontrados? (s/n): ").lower()

    if resposta != 's':
        print("\n❌ Operação cancelada pelo usuário.")
        return

    # 3. Corrigir User id=26
    corrigir_user_26()

    # 4. Criar perfis faltantes
    criar_perfis_faltantes()

    # 5. Verificar signals
    verificar_signals()

    # 6. Diagnóstico final
    print("\n" + "=" * 70)
    print("🎉 DIAGNÓSTICO FINAL")
    print("=" * 70)
    diagnosticar()

    print("\n✅ Script finalizado!")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Tente criar um novo usuário no admin Django")
    print("   2. Se o erro persistir, verifique os signals em accounts/signals.py")
    print("   3. Considere adicionar proteção nos signals (get_or_create)")


if __name__ == "__main__":
    main()

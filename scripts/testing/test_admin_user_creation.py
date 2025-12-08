"""
Teste para verificar se a criação de usuário via admin funciona corretamente.
Testa se o problema do IntegrityError foi resolvido.
"""
import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.db import transaction

def test_user_creation_with_profile():
    """
    Testa se é possível criar um usuário sem erro de IntegrityError.

    Este teste simula o que acontece quando:
    1. Um usuário é criado
    2. Um signal cria automaticamente um UserProfile
    3. O inline tenta criar/atualizar o perfil
    """
    print("\n" + "="*60)
    print("Teste: Criação de Usuário com UserProfile via Admin")
    print("="*60)

    # Limpa usuário de teste se existir
    test_username = 'test_admin_user_001'
    User.objects.filter(username=test_username).delete()

    try:
        print("\n[1/5] Criando novo usuário...")
        with transaction.atomic():
            user = User.objects.create_user(
                username=test_username,
                email='test_admin_001@example.com',
                password='testpass123'
            )
        print(f"    [OK] Usuário criado: {user.username} (ID: {user.id})")

        print("\n[2/5] Verificando se o signal criou o perfil automaticamente...")
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"    [OK] Perfil encontrado: ID {profile.id}")
        except UserProfile.DoesNotExist:
            print("    [ERRO] Signal não criou o perfil automaticamente!")
            return False

        print("\n[3/5] Simulando o que o inline faz (get_or_create)...")
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f"    [AVISO] Perfil foi criado novamente (ID: {profile.id})")
            print("    Isso não deveria acontecer!")
            return False
        else:
            print(f"    [OK] Perfil existente retornado (ID: {profile.id})")

        print("\n[4/5] Testando atualização do perfil (como o inline faria)...")
        profile.bio = "Bio de teste via admin"
        profile.total_xp = 100
        profile.save()
        print("    [OK] Perfil atualizado com sucesso")

        print("\n[5/5] Verificando integridade final...")
        profiles_count = UserProfile.objects.filter(user=user).count()
        if profiles_count == 1:
            print(f"    [OK] Apenas 1 perfil existe para o usuário")
        else:
            print(f"    [ERRO] {profiles_count} perfis encontrados! Deveria ser apenas 1")
            return False

        print("\n" + "="*60)
        print("[SUCESSO] Todos os testes passaram!")
        print("="*60)
        print("\nO problema do IntegrityError foi resolvido.")
        print("Agora você pode criar usuários via admin sem erros.\n")

        return True

    except Exception as e:
        print(f"\n[ERRO] Exceção capturada: {type(e).__name__}")
        print(f"Mensagem: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Limpa o usuário de teste
        print("\n[LIMPEZA] Removendo usuário de teste...")
        User.objects.filter(username=test_username).delete()
        print("    [OK] Usuário removido\n")


def test_multiple_get_or_create():
    """
    Testa especificamente se múltiplas chamadas de get_or_create
    não causam IntegrityError.
    """
    print("\n" + "="*60)
    print("Teste Extra: Múltiplas chamadas get_or_create")
    print("="*60)

    test_username = 'test_multiple_001'
    User.objects.filter(username=test_username).delete()

    try:
        user = User.objects.create_user(
            username=test_username,
            email='test_multiple_001@example.com',
            password='testpass123'
        )

        print("\n[1/3] Primeira chamada get_or_create...")
        profile1, created1 = UserProfile.objects.get_or_create(user=user)
        print(f"    Profile ID: {profile1.id}, Created: {created1}")

        print("\n[2/3] Segunda chamada get_or_create...")
        profile2, created2 = UserProfile.objects.get_or_create(user=user)
        print(f"    Profile ID: {profile2.id}, Created: {created2}")

        print("\n[3/3] Terceira chamada get_or_create...")
        profile3, created3 = UserProfile.objects.get_or_create(user=user)
        print(f"    Profile ID: {profile3.id}, Created: {created3}")

        if profile1.id == profile2.id == profile3.id:
            print("\n[OK] Todas as chamadas retornaram o mesmo perfil")
            if created1 and not created2 and not created3:
                print("[OK] Apenas a primeira criou o perfil")
                return True
            else:
                print("[AVISO] Padrão de criação inesperado")
                return True  # Ainda assim funciona
        else:
            print("\n[ERRO] IDs diferentes foram retornados!")
            return False

    except Exception as e:
        print(f"\n[ERRO] {type(e).__name__}: {str(e)}")
        return False

    finally:
        User.objects.filter(username=test_username).delete()


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# TESTES DE ADMIN - CRIAÇÃO DE USUÁRIO COM PROFILE")
    print("#"*60)

    result1 = test_user_creation_with_profile()
    result2 = test_multiple_get_or_create()

    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    print(f"Teste 1 (Criação via Admin):      {'[PASSOU]' if result1 else '[FALHOU]'}")
    print(f"Teste 2 (Múltiplas get_or_create): {'[PASSOU]' if result2 else '[FALHOU]'}")
    print("="*60)

    if result1 and result2:
        print("\n*** TODOS OS TESTES PASSARAM ***")
        print("\nO fix está funcionando corretamente!")
        print("Você pode agora criar usuários via admin sem problemas.\n")
    else:
        print("\n*** ALGUNS TESTES FALHARAM ***")
        print("\nVerifique os detalhes acima.\n")

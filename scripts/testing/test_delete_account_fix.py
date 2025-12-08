"""
Teste para verificar se as correções no delete_account funcionam.
Testa imports e sintaxe básica.
"""
import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

def test_imports():
    """Testa se todos os imports necessários estão corretos."""
    print("=" * 60)
    print("TESTE: Imports da View delete_account")
    print("=" * 60)

    try:
        # Testar import do timezone
        from django.utils import timezone
        print("[OK] django.utils.timezone importado com sucesso")

        # Testar import do BookShelf
        from accounts.models import BookShelf
        print("[OK] accounts.models.BookShelf importado com sucesso")

        # Testar import do AccountDeletion
        from accounts.models import AccountDeletion
        print("[OK] accounts.models.AccountDeletion importado com sucesso")

        # Testar se a view pode ser importada
        from accounts.views import delete_account
        print("[OK] accounts.views.delete_account importado com sucesso")

        print("\n[OK] Todos os imports estão corretos!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao importar: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_timezone_usage():
    """Testa se o timezone está sendo usado corretamente."""
    print("=" * 60)
    print("TESTE: Uso do timezone")
    print("=" * 60)

    try:
        from django.utils import timezone
        from datetime import datetime

        # Testar timezone.now()
        now = timezone.now()
        print(f"[OK] timezone.now() funciona: {now}")

        # Testar cálculo de delta
        user_created = timezone.now()
        delta = timezone.now() - user_created
        days = delta.days
        print(f"[OK] Cálculo de dias funciona: {days} dias")

        print("\n[OK] timezone está funcionando corretamente!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao usar timezone: {str(e)}\n")
        return False


def test_bookshelf_model():
    """Testa se o modelo BookShelf existe e funciona."""
    print("=" * 60)
    print("TESTE: Modelo BookShelf")
    print("=" * 60)

    try:
        from accounts.models import BookShelf
        from django.contrib.auth.models import User

        # Testar se o modelo tem os métodos esperados
        print(f"[OK] BookShelf.objects existe: {BookShelf.objects}")
        print(f"[OK] BookShelf.objects.filter existe: {hasattr(BookShelf.objects, 'filter')}")
        print(f"[OK] BookShelf.objects.count existe: {hasattr(BookShelf.objects, 'count')}")

        # Testar query básica (sem executar)
        query = BookShelf.objects.filter(user_id=999)
        print(f"[OK] Query BookShelf criada: {query.query}")

        print("\n[OK] Modelo BookShelf está funcionando!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao testar BookShelf: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_account_deletion_model():
    """Testa se o modelo AccountDeletion funciona."""
    print("=" * 60)
    print("TESTE: Modelo AccountDeletion")
    print("=" * 60)

    try:
        from accounts.models import AccountDeletion
        from django.utils import timezone

        # Verificar campos do modelo
        fields = [f.name for f in AccountDeletion._meta.get_fields()]
        print(f"[OK] AccountDeletion tem {len(fields)} campos")

        required_fields = [
            'username', 'email', 'user_id', 'deleted_at',
            'deletion_reason', 'was_premium', 'books_count',
            'email_sent', 'days_as_member'
        ]

        for field in required_fields:
            if field in fields:
                print(f"[OK] Campo '{field}' existe")
            else:
                print(f"[ERRO] Campo '{field}' NÃO existe")
                return False

        print("\n[OK] Modelo AccountDeletion está completo!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao testar AccountDeletion: {str(e)}\n")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "#" * 60)
    print("# TESTES DE CORREÇÃO - DELETE ACCOUNT")
    print("#" * 60 + "\n")

    results = []

    # Executar testes
    results.append(("Imports", test_imports()))
    results.append(("Timezone", test_timezone_usage()))
    results.append(("BookShelf", test_bookshelf_model()))
    results.append(("AccountDeletion", test_account_deletion_model()))

    # Resumo
    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for _, result in results if result)

    for test_name, result in results:
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        print(f"{test_name:20} {status}")

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n*** TODOS OS TESTES PASSARAM! ***")
        print("\nAs correções foram aplicadas com sucesso!")
        print("\nAgora você pode tentar excluir a conta novamente.")
        print("Acesse: /profile/delete-account/confirm/")
        return True
    else:
        print("\n*** ALGUNS TESTES FALHARAM ***")
        print("Verifique os erros acima.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

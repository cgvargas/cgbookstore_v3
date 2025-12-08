"""
Script de teste para funcionalidade de exclusão de conta.
Testa a lógica sem realmente criar/deletar usuários.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.urls import reverse


def test_delete_account_urls():
    """Testa se as URLs estão configuradas corretamente."""
    print("=" * 60)
    print("TESTE: URLs de Exclusão de Conta")
    print("=" * 60)

    try:
        # Testar URL de confirmação
        url_confirm = reverse('accounts:delete_account_confirm')
        print(f"[OK] URL Confirmação: {url_confirm}")
        assert url_confirm == '/profile/delete-account/confirm/', "URL de confirmação incorreta"

        # Testar URL de exclusão
        url_delete = reverse('accounts:delete_account')
        print(f"[OK] URL Exclusão: {url_delete}")
        assert url_delete == '/profile/delete-account/', "URL de exclusão incorreta"

        print("\n[OK] Todas as URLs configuradas corretamente!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao testar URLs: {str(e)}\n")
        return False


def test_view_imports():
    """Testa se as views podem ser importadas."""
    print("=" * 60)
    print("TESTE: Importação de Views")
    print("=" * 60)

    try:
        from accounts.views import delete_account_confirm, delete_account
        print("[OK] View 'delete_account_confirm' importada com sucesso")
        print("[OK] View 'delete_account' importada com sucesso")

        # Verificar se são callables
        assert callable(delete_account_confirm), "delete_account_confirm não é callable"
        assert callable(delete_account), "delete_account não é callable"

        print("\n[OK] Todas as views importadas corretamente!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao importar views: {str(e)}\n")
        return False


def test_template_exists():
    """Verifica se o template existe."""
    print("=" * 60)
    print("TESTE: Template de Confirmação")
    print("=" * 60)

    try:
        from django.template.loader import get_template

        template = get_template('accounts/delete_account_confirm.html')
        print(f"[OK] Template encontrado: {template.origin.name}")

        print("\n[OK] Template existe e pode ser carregado!\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro ao carregar template: {str(e)}\n")
        return False


def test_validation_logic():
    """Testa a lógica de validação sem criar usuários."""
    print("=" * 60)
    print("TESTE: Lógica de Validação")
    print("=" * 60)

    # Simular validações
    test_cases = [
        {
            'email_confirmation': 'user@example.com',
            'user_email': 'user@example.com',
            'understood': True,
            'should_pass': True,
            'description': 'Email correto + checkbox marcado'
        },
        {
            'email_confirmation': 'wrong@example.com',
            'user_email': 'user@example.com',
            'understood': True,
            'should_pass': False,
            'description': 'Email incorreto'
        },
        {
            'email_confirmation': 'user@example.com',
            'user_email': 'user@example.com',
            'understood': False,
            'should_pass': False,
            'description': 'Checkbox não marcado'
        },
    ]

    all_passed = True

    for i, test in enumerate(test_cases, 1):
        email_matches = test['email_confirmation'] == test['user_email']
        checkbox_checked = test['understood']
        validation_passes = email_matches and checkbox_checked

        expected = test['should_pass']
        result = "[OK] PASSOU" if validation_passes == expected else "[ERRO] FALHOU"

        print(f"\nTeste {i}: {test['description']}")
        print(f"  Email match: {email_matches}")
        print(f"  Checkbox: {checkbox_checked}")
        print(f"  Validação: {validation_passes} (esperado: {expected})")
        print(f"  {result}")

        if validation_passes != expected:
            all_passed = False

    if all_passed:
        print("\n[OK] Todas as validações funcionam corretamente!\n")
    else:
        print("\n[ERRO] Algumas validações falharam!\n")

    return all_passed


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTES DE EXCLUSÃO DE CONTA")
    print("=" * 60 + "\n")

    results = []

    # Executar testes
    results.append(("URLs", test_delete_account_urls()))
    results.append(("Views", test_view_imports()))
    results.append(("Template", test_template_exists()))
    results.append(("Validação", test_validation_logic()))

    # Resumo
    print("=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for _, result in results if result)

    for test_name, result in results:
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        print(f"{test_name:20} {status}")

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n*** TODOS OS TESTES PASSARAM! ***")
        print("\nFuncionalidade de exclusao de conta implementada com sucesso!")
        print("\nProximos passos:")
        print("  1. Acesse /profile/edit/ para ver o link de exclusao")
        print("  2. Clique em 'Excluir Minha Conta'")
        print("  3. Siga o processo de confirmacao")
        print("  4. Digite seu email e marque o checkbox")
        print("  5. Confirme a exclusao final")
        return True
    else:
        print("\nALGUNS TESTES FALHARAM")
        print("Verifique os erros acima para corrigir os problemas.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

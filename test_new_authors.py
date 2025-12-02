"""
Script de teste rapido para o modulo de Autores Emergentes e Editoras
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from new_authors.models import (
    EmergingAuthor, AuthorBook, Chapter,
    PublisherProfile, PublisherInterest
)

def test_models():
    """Testa se os modelos estão funcionando"""
    print("=" * 60)
    print("TESTANDO MODELOS")
    print("=" * 60)

    # Contar registros
    authors = EmergingAuthor.objects.count()
    books = AuthorBook.objects.count()
    chapters = Chapter.objects.count()
    publishers = PublisherProfile.objects.count()

    print(f"✓ Autores Emergentes: {authors}")
    print(f"✓ Livros: {books}")
    print(f"✓ Capítulos: {chapters}")
    print(f"✓ Editoras: {publishers}")

    # Livros publicados
    published = AuthorBook.objects.filter(status='published').count()
    print(f"✓ Livros Publicados: {published}")

    return True

def test_urls():
    """Testa se as URLs estão configuradas"""
    print("\n" + "=" * 60)
    print("TESTANDO URLS")
    print("=" * 60)

    from django.urls import reverse, NoReverseMatch

    urls_to_test = [
        ('new_authors:books_list', {}),
        ('new_authors:become_author', {}),
        ('new_authors:become_publisher', {}),
        ('new_authors:author_dashboard', {}),
        ('new_authors:publisher_dashboard', {}),
    ]

    for url_name, kwargs in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✓ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"✗ {url_name}: ERRO - {e}")
            return False

    return True

def test_permissions():
    """Testa permissões básicas"""
    print("\n" + "=" * 60)
    print("TESTANDO PERMISSÕES")
    print("=" * 60)

    # Verificar se há usuários
    users = User.objects.count()
    print(f"✓ Total de usuários: {users}")

    # Verificar autores
    authors_with_users = EmergingAuthor.objects.select_related('user').count()
    print(f"✓ Autores com usuários: {authors_with_users}")

    # Verificar editoras verificadas
    verified_publishers = PublisherProfile.objects.filter(is_verified=True).count()
    print(f"✓ Editoras verificadas: {verified_publishers}")

    return True

def main():
    """Executa todos os testes"""
    print("\n*** INICIANDO TESTES DO MODULO DE AUTORES EMERGENTES ***\n")

    results = []

    try:
        results.append(("Modelos", test_models()))
    except Exception as e:
        print(f"✗ ERRO nos modelos: {e}")
        results.append(("Modelos", False))

    try:
        results.append(("URLs", test_urls()))
    except Exception as e:
        print(f"✗ ERRO nas URLs: {e}")
        results.append(("URLs", False))

    try:
        results.append(("Permissões", test_permissions()))
    except Exception as e:
        print(f"✗ ERRO nas permissões: {e}")
        results.append(("Permissões", False))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n[OK] TODOS OS TESTES PASSARAM!")
    else:
        print("\n[AVISO] ALGUNS TESTES FALHARAM - REVISAR PROBLEMAS")

    return all_passed

if __name__ == '__main__':
    main()

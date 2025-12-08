# coding: utf-8
"""
Script para verificar perfis do usuario atual
"""

from django.contrib.auth import get_user_model
from new_authors.models import EmergingAuthor, PublisherProfile

User = get_user_model()

# Pegar o superusuario
superuser = User.objects.filter(is_superuser=True).first()

if superuser:
    print(f"\nVerificando perfis do usuario: {superuser.username}")
    print("=" * 60)

    # Verificar perfil de autor emergente
    try:
        author_profile = superuser.emerging_author_profile
        print(f"\nPerfil de Autor Emergente encontrado:")
        print(f"   - Nome: {author_profile}")
        print(f"   - Bio: {author_profile.bio[:50] if author_profile.bio else 'Vazio'}...")
        has_author = True
    except EmergingAuthor.DoesNotExist:
        print(f"\nPerfil de Autor Emergente NAO encontrado")
        has_author = False

    # Verificar perfil de editora
    try:
        publisher_profile = superuser.publisher_profile
        print(f"\nPerfil de Editora encontrado:")
        print(f"   - Nome: {publisher_profile.company_name}")
        has_publisher = True
    except PublisherProfile.DoesNotExist:
        print(f"\nPerfil de Editora NAO encontrado")
        has_publisher = False

    print("\n" + "=" * 60)
    print("RESULTADO:")
    print("=" * 60)

    if has_publisher and has_author:
        print("\nUsuario tem AMBOS os perfis (Autor E Editora)")
        print("Agora o navbar mostrara:")
        print("   - 'Meu Dashboard' (para autor)")
        print("   - 'Dashboard Editora' (para editora)")
        print("\nAmbos os dashboards aparecem no navbar!")

    elif has_publisher and not has_author:
        print("\nApenas perfil de Editora existe")
        print("'Dashboard Editora' aparecera no navbar")

    elif has_author and not has_publisher:
        print("\nApenas perfil de Autor Emergente existe")
        print("'Meu Dashboard' aparecera no navbar")

    else:
        print("\nNenhum perfil encontrado!")

else:
    print("\nNenhum superusuario encontrado!")

print("\n" + "=" * 60)

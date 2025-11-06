#!/usr/bin/env python
"""
Script para criar apps sociais com credenciais placeholder
Isso fará os botões aparecerem, mas eles não funcionarão até você
adicionar as credenciais reais no Django Admin.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Obter site atual
site = Site.objects.get_current()

print("=" * 60)
print("CONFIGURANDO APPS SOCIAIS (PLACEHOLDER)")
print("=" * 60)
print()

# Remover apps existentes
SocialApp.objects.all().delete()
print("[INFO] Apps sociais anteriores removidos")

# Configurar Google (placeholder)
google_app = SocialApp.objects.create(
    provider='google',
    name='Google Login',
    client_id='CONFIGURE_NO_ADMIN',  # Placeholder
    secret='CONFIGURE_NO_ADMIN',  # Placeholder
)
google_app.sites.add(site)
print("[OK] Google app criado (credenciais placeholder)")

# Configurar Facebook (placeholder)
facebook_app = SocialApp.objects.create(
    provider='facebook',
    name='Facebook Login',
    client_id='CONFIGURE_NO_ADMIN',  # Placeholder
    secret='CONFIGURE_NO_ADMIN',  # Placeholder
)
facebook_app.sites.add(site)
print("[OK] Facebook app criado (credenciais placeholder)")

print()
print("=" * 60)
print("BOTOES SOCIAIS AGORA VISIVEIS NAS PAGINAS!")
print("=" * 60)
print()
print("Os botoes aparecerão nas páginas de login e cadastro,")
print("mas não funcionarão até você configurar as credenciais reais.")
print()
print("Para configurar as credenciais:")
print("1. Acesse: http://localhost:8000/admin/")
print("2. Vá em 'Social applications'")
print("3. Edite cada app e adicione as credenciais reais")
print()
print("Ou siga o guia: CONFIGURAR_LOGIN_SOCIAL.md")
print()

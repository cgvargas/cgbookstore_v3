# -*- coding: utf-8 -*-
"""
Script para testar envio de email HTML de confirmação
"""
import os
import sys
import django

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from accounts.adapters import CustomAccountAdapter
from django.test import RequestFactory

print("=" * 70)
print("TESTE: EMAIL HTML DE CONFIRMAÇÃO")
print("=" * 70)

# Criar usuário de teste (se não existir)
username = "test_html_email"
email_dest = "claudio.g.vargas@outlook.com"

print(f"\n[1] Procurando/criando usuário de teste: {username}")

try:
    user = User.objects.get(username=username)
    print(f"[OK] Usuário já existe: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=username,
        email=email_dest,
        password='testpass123'
    )
    print(f"[OK] Usuário criado: {user.username}")

# Garantir que EmailAddress existe
email_address, created = EmailAddress.objects.get_or_create(
    user=user,
    email=user.email,
    defaults={'primary': True, 'verified': False}
)
if created:
    print(f"[OK] EmailAddress criado para {user.email}")
else:
    print(f"[OK] EmailAddress já existe para {user.email}")

# Criar confirmação HMAC
print(f"\n[2] Gerando link de confirmação...")
from allauth.account.utils import user_pk_to_url_str
confirmation = EmailConfirmationHMAC(email_address)
# Gerar a key e construir URL manualmente
key = confirmation.key
activate_url = f"http://localhost:8000/accounts/confirm-email/{key}/"
print(f"[OK] Link gerado: {activate_url[:60]}...")

# Preparar contexto para o template
print(f"\n[3] Preparando contexto do email...")
site = Site.objects.get_current()
context = {
    'user': user,
    'activate_url': activate_url,
    'expiration_days': 3,
    'site_name': site.name,
    'site_domain': site.domain,
    'current_year': 2025,
}
print(f"[OK] Contexto preparado com site: {site.name}")

# Enviar email usando o adapter customizado
print(f"\n[4] Enviando email HTML via CustomAccountAdapter...")
print(f"    Destinatário: {email_dest}")
print("    Aguarde...")

try:
    adapter = CustomAccountAdapter()
    request = RequestFactory().get('/')

    adapter.send_mail(
        template_prefix='account/email/email_confirmation',
        email=email_dest,
        context=context
    )

    print(f"\n[OK] Email enviado com sucesso!")
    print(f"[INFO] Verifique sua caixa de entrada: {email_dest}")
    print(f"[INFO] O email deve ter um botão clicável e estar formatado em HTML")

except Exception as e:
    print(f"\n[ERRO] Falha ao enviar email: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIM DO TESTE")
print("=" * 70)
print("\n[INSTRUÇÕES]")
print("1. Verifique sua caixa de entrada")
print("2. O email deve estar bonito com gradiente roxo")
print("3. Deve ter um botão 'Confirmar meu Email' clicável")
print("4. Se clicar no botão ou link, deve levar à página de confirmação")

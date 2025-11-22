# -*- coding: utf-8 -*-
"""
Script para debugar o fluxo de login e verificacao de email
"""
import os
import sys
import django

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

print("=" * 70)
print("DEBUG: FLUXO DE LOGIN E VERIFICACAO")
print("=" * 70)

# Verificar usuario especifico
email = 'claudio.g.vargas@outlook.com'

print(f"\nVerificando usuario: {email}")
print("-" * 70)

try:
    user = User.objects.get(email=email)
    print(f"[OK] Usuario encontrado no User model:")
    print(f"   - Username: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - is_active: {user.is_active}")
    print(f"   - is_staff: {user.is_staff}")
    print(f"   - last_login: {user.last_login}")
except User.DoesNotExist:
    print(f"[ERRO] Usuario NAO encontrado no User model")
    user = None

if user:
    print(f"\nVerificando EmailAddress records:")
    print("-" * 70)

    email_addresses = EmailAddress.objects.filter(user=user)

    if email_addresses.exists():
        for ea in email_addresses:
            status = "[VERIFICADO]" if ea.verified else "[NAO VERIFICADO]"
            primary = "[PRIMARY]" if ea.primary else "[secundario]"
            print(f"   {status} {primary}")
            print(f"   - Email: {ea.email}")
            print(f"   - Verified: {ea.verified}")
            print(f"   - Primary: {ea.primary}")
            print()
    else:
        print("   [ERRO] NENHUM EmailAddress record encontrado!")
        print("   [PROBLEMA] User existe mas nao tem EmailAddress")
        print("   [SOLUCAO] Criar EmailAddress record manualmente")

# Verificar configuracao do allauth
print("\nConfiguracoes do django-allauth:")
print("-" * 70)

from django.conf import settings

print(f"   - ACCOUNT_EMAIL_VERIFICATION: {settings.ACCOUNT_EMAIL_VERIFICATION}")
print(f"   - ACCOUNT_EMAIL_REQUIRED: {getattr(settings, 'ACCOUNT_EMAIL_REQUIRED', 'NOT SET')}")
print(f"   - ACCOUNT_UNIQUE_EMAIL: {getattr(settings, 'ACCOUNT_UNIQUE_EMAIL', 'NOT SET')}")
print(f"   - ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS: {getattr(settings, 'ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS', 'NOT SET')}")

# Verificar se ha inconsistencias
print("\nProcurando inconsistencias no banco:")
print("-" * 70)

users_sem_email = []
for u in User.objects.all():
    if not EmailAddress.objects.filter(user=u).exists():
        users_sem_email.append(u)

if users_sem_email:
    print(f"   [ALERTA] {len(users_sem_email)} usuarios SEM EmailAddress record:")
    for u in users_sem_email:
        print(f"      - {u.username} ({u.email})")
else:
    print("   [OK] Todos os usuarios tem EmailAddress records")

# Verificar emails nao verificados
unverified = EmailAddress.objects.filter(verified=False)
if unverified.exists():
    print(f"\n   [ALERTA] {unverified.count()} emails NAO VERIFICADOS:")
    for ea in unverified:
        print(f"      - {ea.email} (user: {ea.user.username})")
else:
    print("\n   [OK] Todos os emails estao verificados")

# Verificar emails nao-primary
non_primary = EmailAddress.objects.filter(primary=False)
if non_primary.exists():
    print(f"\n   [ALERTA] {non_primary.count()} emails NAO sao PRIMARY:")
    for ea in non_primary:
        print(f"      - {ea.email} (user: {ea.user.username}, verified: {ea.verified})")

print("\n" + "=" * 70)
print("FIM DO DEBUG")
print("=" * 70)

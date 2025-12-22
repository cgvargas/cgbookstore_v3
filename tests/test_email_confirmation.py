"""
Script de teste para verificar configuração de email.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress, EmailConfirmation

print("="*60)
print("TESTE DE CONFIGURAÇÃO DE EMAIL")
print("="*60)

# Verificar configurações
print("\n1. CONFIGURAÇÕES DE EMAIL:")
print(f"   Backend: {settings.EMAIL_BACKEND}")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Port: {settings.EMAIL_PORT}")
print(f"   TLS: {settings.EMAIL_USE_TLS}")
print(f"   User: {settings.EMAIL_HOST_USER or '(não configurado)'}")
print(f"   From: {settings.DEFAULT_FROM_EMAIL}")

# Verificar django-allauth
print("\n2. CONFIGURAÇÕES ALLAUTH:")
print(f"   Email obrigatório: {settings.ACCOUNT_EMAIL_REQUIRED}")
print(f"   Email único: {settings.ACCOUNT_UNIQUE_EMAIL}")
print(f"   Verificação: {settings.ACCOUNT_EMAIL_VERIFICATION}")
print(f"   Expiração: {settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS} dias")

# Teste de envio simples
print("\n3. TESTE DE ENVIO SIMPLES:")
print("   Tentando enviar email de teste...")

try:
    send_mail(
        subject='[CGBookStore] Teste de Configuração',
        message='Este é um email de teste para verificar a configuração SMTP.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['teste@example.com'],  # Mude para seu email
        fail_silently=False,
    )
    print("   OK Email enviado com sucesso!")
    if 'console' in settings.EMAIL_BACKEND:
        print("   INFO Verifique o console/terminal para ver o email")
    else:
        print("   INFO Verifique sua caixa de entrada")
except Exception as e:
    print(f"   ERRO ao enviar email: {e}")

# Verificar usuários sem email confirmado
print("\n4. USUÁRIOS SEM EMAIL CONFIRMADO:")
unverified_users = User.objects.filter(
    emailaddress__verified=False
).distinct()

if unverified_users.exists():
    print(f"   Encontrados {unverified_users.count()} usuário(s) sem confirmação:")
    for user in unverified_users[:5]:
        email_addr = EmailAddress.objects.filter(user=user).first()
        if email_addr:
            print(f"     - {user.username} ({email_addr.email})")
else:
    print("   INFO Nenhum usuario pendente de confirmacao")

# Verificar links de confirmação pendentes
print("\n5. LINKS DE CONFIRMAÇÃO ATIVOS:")
active_confirmations = EmailConfirmation.objects.filter(
    email_address__verified=False
)

if active_confirmations.exists():
    print(f"   Encontrados {active_confirmations.count()} link(s) ativo(s):")
    for conf in active_confirmations[:5]:
        print(f"     - {conf.email_address.email}")
        print(f"       Key: {conf.key}")
        print(f"       Enviado em: {conf.sent}")
else:
    print("   INFO Nenhum link de confirmacao ativo")

print("\n" + "="*60)
print("TESTE CONCLUIDO")
print("="*60)

# Instruções
print("\nPROXIMOS PASSOS:")
if 'console' in settings.EMAIL_BACKEND:
    print("   1. Para testar em producao, configure EMAIL_BACKEND no .env")
    print("   2. Adicione EMAIL_HOST_USER e EMAIL_HOST_PASSWORD")
    print("   3. Reinicie o servidor")
else:
    print("   1. OK Email configurado para producao")
    print("   2. Teste criando um novo usuario")
    print("   3. Verifique se o email de confirmacao chega")

print("\nDocumentacao completa: docs/CONFIGURAR_EMAIL.md")

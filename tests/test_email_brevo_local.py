# -*- coding: utf-8 -*-
"""
Script para testar envio de email via Brevo em desenvolvimento local
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

from django.core.mail import send_mail
from django.conf import settings

print("=" * 70)
print("TESTE DE EMAIL - BREVO API (Desenvolvimento Local)")
print("=" * 70)

print("\n[1] Verificando configuracoes:")
print("-" * 70)
print(f"   - USE_BREVO_API: {getattr(settings, 'USE_BREVO_API', 'NOT SET')}")
print(f"   - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"   - BREVO_API_KEY configurada: {'Sim' if os.environ.get('EMAIL_HOST_PASSWORD') else 'Nao'}")

if settings.EMAIL_BACKEND == 'cgbookstore.backends.brevo.BrevoBackend':
    print("\n[OK] Backend configurado para Brevo API")
elif settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("\n[AVISO] Backend configurado para CONSOLE (emails aparecem no terminal)")
    print("        Para testar Brevo, configure USE_BREVO_API=True no .env")
else:
    print(f"\n[INFO] Backend: {settings.EMAIL_BACKEND}")

print("\n[2] Enviando email de teste:")
print("-" * 70)

# Email de destino para teste (pegando do argumento ou usando padrão)
if len(sys.argv) > 1:
    destinatario = sys.argv[1]
else:
    destinatario = 'claudio.g.vargas@outlook.com'

print(f"\n   Enviando para: {destinatario}")
print("   (Use: python test_email_brevo_local.py seuemail@exemplo.com para mudar)")
print("   Aguarde...")

try:
    result = send_mail(
        subject='[TESTE] Email de Desenvolvimento - CGBookStore',
        message=(
            'Olá!\n\n'
            'Este é um email de teste enviado do ambiente de DESENVOLVIMENTO LOCAL '
            'do CGBookStore via Brevo API.\n\n'
            'Se você recebeu esta mensagem, significa que:\n'
            '✓ Brevo API está configurado corretamente\n'
            '✓ Email remetente está verificado\n'
            '✓ Sistema de email funcionando perfeitamente\n\n'
            'Configuração:\n'
            f'- Backend: {settings.EMAIL_BACKEND}\n'
            f'- Remetente: {settings.DEFAULT_FROM_EMAIL}\n'
            f'- Ambiente: Desenvolvimento Local\n\n'
            'Atenciosamente,\n'
            'Sistema CGBookStore'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinatario],
        fail_silently=False,
    )

    if result == 1:
        print("\n" + "=" * 70)
        print("[SUCESSO] Email enviado com sucesso!")
        print("=" * 70)
        print(f"\nVerifique a caixa de entrada de: {destinatario}")
        print("(pode levar alguns segundos para chegar)")

        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print("\n[INFO] Como esta usando console backend, o email apareceu acima")
        else:
            print("\n[INFO] Email enviado via Brevo API")
            print("      Você pode verificar no dashboard do Brevo:")
            print("      https://app.brevo.com/log/email")
    else:
        print("\n[ERRO] Falha ao enviar email (result != 1)")

except Exception as e:
    print("\n" + "=" * 70)
    print("[ERRO] Falha ao enviar email")
    print("=" * 70)
    print(f"\nDetalhes do erro:")
    print(f"{type(e).__name__}: {str(e)}")

    if "401" in str(e) or "Unauthorized" in str(e):
        print("\n[CAUSA PROVAVEL] API Key invalida ou expirada")
        print("   Solucao: Verifique EMAIL_HOST_PASSWORD no .env")
    elif "Sender" in str(e) or "sender" in str(e):
        print("\n[CAUSA PROVAVEL] Email remetente nao verificado no Brevo")
        print("   Solucao: Adicione e verifique o email em:")
        print("   https://app.brevo.com/senders")
    elif "sib_api_v3_sdk" in str(e):
        print("\n[CAUSA PROVAVEL] Biblioteca sib-api-v3-sdk nao instalada")
        print("   Solucao: pip install sib-api-v3-sdk")

    import traceback
    print("\n[STACK TRACE]")
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIM DO TESTE")
print("=" * 70)

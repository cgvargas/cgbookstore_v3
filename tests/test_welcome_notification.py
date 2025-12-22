# -*- coding: utf-8 -*-
"""
Script para testar notificação de boas-vindas
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
from accounts.models.reading_notification import SystemNotification
from allauth.account.models import EmailAddress

print("=" * 70)
print("TESTE: NOTIFICACAO DE BOAS-VINDAS")
print("=" * 70)

# Criar usuário de teste
username = f"test_user_{os.urandom(4).hex()}"
email = f"{username}@test.com"

print(f"\nCriando usuario de teste: {username}")
print(f"Email: {email}")

try:
    # Criar usuário (signal deve disparar automaticamente)
    user = User.objects.create_user(
        username=username,
        email=email,
        password='testpass123'
    )

    print(f"\n[OK] Usuario criado: {user.username}")

    # Verificar UserProfile
    try:
        profile = user.userprofile
        print(f"[OK] UserProfile criado: Level {profile.level}, XP {profile.total_xp}")
    except Exception as e:
        print(f"[ERRO] UserProfile nao encontrado: {e}")

    # Verificar EmailAddress
    email_addr = EmailAddress.objects.filter(user=user).first()
    if email_addr:
        print(f"[OK] EmailAddress criado: {email_addr.email} (verified={email_addr.verified})")
    else:
        print("[AVISO] EmailAddress nao encontrado")

    # Verificar notificação
    notifications = SystemNotification.objects.filter(user=user)
    print(f"\n[NOTIFICACOES] Total: {notifications.count()}")

    for notif in notifications:
        print(f"\n  Tipo: {notif.get_notification_type_display()}")
        print(f"  Mensagem: {notif.message[:100]}...")
        print(f"  Prioridade: {notif.priority}")
        print(f"  Lida: {notif.is_read}")
        print(f"  Action URL: {notif.action_url}")
        print(f"  Action Text: {notif.action_text}")

    if notifications.exists():
        print("\n[OK] Notificacao de boas-vindas criada com sucesso!")
    else:
        print("\n[ERRO] Nenhuma notificacao foi criada!")

    # Cleanup
    print(f"\n[CLEANUP] Deletando usuario de teste...")
    user.delete()
    print("[OK] Usuario deletado")

except Exception as e:
    print(f"\n[ERRO] Falha ao criar usuario: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIM DO TESTE")
print("=" * 70)

"""
Script temporário para criar superusuário.
Execute UMA VEZ e depois delete este arquivo.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# ALTERE AQUI COM SUAS CREDENCIAIS
username = 'admin'
email = 'seu@email.com'  # ← ALTERE
password = 'SuaSenhaSegura123'  # ← ALTERE

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superusuário criado: {username} / {email}')
else:
    print(f'⚠️ Usuário {username} já existe')

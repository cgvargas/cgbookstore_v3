# -*- coding: utf-8 -*-
"""
Script de teste: envia e-mail de boas-vindas Premium com badge
para claudio.g.vargas@gmail.com
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

django.setup()

from django.utils import timezone
from datetime import timedelta
from finance.email_service import PremiumEmailService
from finance.badge_service import get_premium_badge_context


class FakeUser:
    """Usuario simulado para teste sem gravar no banco."""
    username = 'Claudio Vargas'
    email = 'claudio.g.vargas@gmail.com'

    def get_full_name(self):
        return 'Claudio Vargas'


def main():
    user = FakeUser()
    expires_at = timezone.now() + timedelta(days=30)
    badge_context = get_premium_badge_context()

    print("Badge context:")
    for k, v in badge_context.items():
        print(f"  {k}: {v}")

    print(f"\nEnviando e-mail para: {user.email}")

    result = PremiumEmailService.send_welcome_email(
        user=user,
        expires_at=expires_at,
        price='9,90',
        badge_context=badge_context,
        is_free_campaign=False
    )

    if result:
        print("SUCESSO! E-mail enviado.")
    else:
        print("FALHOU. Verifique os logs acima.")


if __name__ == '__main__':
    main()

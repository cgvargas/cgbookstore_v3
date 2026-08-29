# -*- coding: utf-8 -*-
"""
Script: Cria os badges de Debate e Quiz no banco de dados
e verifica a instalacao.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from finance.badge_service import (
    _ensure_badge_exists,
    PREMIUM_BADGE_CONFIG,
    DEBATE_BADGE_CONFIG,
    QUIZ_BADGE_CONFIG,
)
from accounts.models import Badge

def main():
    print("=" * 60)
    print("CRIANDO/VERIFICANDO BADGES NO BANCO DE DADOS")
    print("=" * 60)

    configs = [PREMIUM_BADGE_CONFIG, DEBATE_BADGE_CONFIG, QUIZ_BADGE_CONFIG]
    for config in configs:
        badge = _ensure_badge_exists(config)
        print(f"  {config['icon']} [{badge.id:>3}] {badge.name}")
        print(f"       slug={badge.slug} | raridade={badge.rarity} | cat={badge.category}")

    print()
    print("=" * 60)
    print("TODOS OS BADGES ATIVOS NO SISTEMA:")
    print("=" * 60)
    for b in Badge.objects.filter(is_active=True).order_by('display_order'):
        print(f"  {b.icon} [{b.id:>3}] {b.name} ({b.get_rarity_display()}) — {b.category}")

    print()
    print("=" * 60)
    print("ONDE OS BADGES SAO CONCEDIDOS:")
    print("=" * 60)
    print("  Membro Premium  -> Subscription.activate()  [finance/models.py]")
    print("  Voz do Debate   -> create_topic() e create_post()  [debates/views.py]")
    print("  Mestre do Quiz  -> submit_quiz()  [news/views.py]")
    print()
    print("Acesse: http://localhost:8000/gamificacao/badges/")

if __name__ == '__main__':
    main()

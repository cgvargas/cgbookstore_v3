# -*- coding: utf-8 -*-
"""
Script: Concede o badge Premium Membro ao usuario real do banco de dados
e exibe as URLs corretas de acesso.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from finance.badge_service import grant_premium_badge, ensure_premium_badge_exists
from accounts.models import UserBadge, Badge

def main():
    # Listar usuarios existentes
    print("=" * 60)
    print("USUARIOS NO BANCO DE DADOS:")
    print("=" * 60)
    users = User.objects.all().order_by('-is_superuser', '-date_joined')
    for u in users:
        premium_flag = ""
        try:
            if hasattr(u, 'profile') and u.profile.is_premium:
                premium_flag = " [PREMIUM]"
            elif hasattr(u, 'subscription') and u.subscription.is_active():
                premium_flag = " [PREMIUM via Subscription]"
        except Exception:
            pass
        print(f"  ID={u.id} | {u.username} | {u.email} | staff={u.is_staff}{premium_flag}")

    print()

    # Conceder badge a todos os usuarios premium (ou ao primeiro superuser)
    badge = ensure_premium_badge_exists()
    print(f"Badge: {badge.name} (slug={badge.slug}, id={badge.id})")
    print()

    # Verificar usuarios com premium ativo
    granted_to = []

    # Tentar pelo subscription ativo
    from finance.models import Subscription
    active_subs = Subscription.objects.filter(status='ativa')
    for sub in active_subs:
        user_badge, created = grant_premium_badge(sub.user)
        if created:
            print(f"[NOVO] Badge concedido a: {sub.user.username} ({sub.user.email})")
        else:
            print(f"[JA TINHA] {sub.user.username} ({sub.user.email})")
        granted_to.append(sub.user.username)

    # Se nao havia nenhuma subscription ativa, conceder a todos os superusers
    if not granted_to:
        superusers = User.objects.filter(is_superuser=True)
        for su in superusers:
            user_badge, created = grant_premium_badge(su)
            if created:
                print(f"[NOVO] Badge concedido ao superuser: {su.username} ({su.email})")
            else:
                print(f"[JA TINHA] {su.username} ({su.email})")
            granted_to.append(su.username)

    # Se ainda nao conseguiu, listar quem tem badge agora
    print()
    print("=" * 60)
    print("USUARIOS COM BADGE 'Membro Premium':")
    print("=" * 60)
    user_badges = UserBadge.objects.filter(badge=badge).select_related('user')
    for ub in user_badges:
        print(f"  {ub.user.username} ({ub.user.email}) - desde {ub.earned_at.strftime('%d/%m/%Y %H:%M')}")

    print()
    print("=" * 60)
    print("URLs CORRETAS:")
    print("=" * 60)
    print("  Coleção de badges:    http://localhost:8000/gamificacao/badges/")
    print("  Dashboard gamif:      http://localhost:8000/gamificacao/")
    print("  Conquistas:           http://localhost:8000/gamificacao/conquistas/")
    print("  Ranking:              http://localhost:8000/gamificacao/ranking/")
    print("  Admin:                http://localhost:8000/admin/")
    print("=" * 60)

if __name__ == '__main__':
    main()

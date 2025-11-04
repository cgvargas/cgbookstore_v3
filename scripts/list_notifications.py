"""
Script para listar notificações de campanhas
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import CampaignNotification

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def list_notifications():
    """Lista todas as notificações de campanhas"""

    print("=" * 70)
    print("NOTIFICAÇÕES DE CAMPANHAS")
    print("=" * 70)
    print()

    notifs = CampaignNotification.objects.all().order_by('-created_at')

    print(f"📬 Total: {notifs.count()} notificação(ões)\n")

    if notifs.count() == 0:
        print("Nenhuma notificação encontrada.")
        return

    for notif in notifs:
        print(f"🔔 Notificação #{notif.id}")
        print(f"   Usuário: {notif.user.username}")
        print(f"   Campanha: {notif.campaign.name if notif.campaign else 'N/A'}")
        print(f"   Tipo: {notif.notification_type}")
        print(f"   Mensagem: {notif.message}")
        print(f"   Prioridade: {notif.priority_name}")
        print(f"   Lida: {'Sim ✓' if notif.is_read else 'Não ●'}")
        print(f"   Criada: {notif.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   Ação: {notif.action_text} → {notif.action_url}")
        print()

    # Estatísticas
    unread = notifs.filter(is_read=False).count()
    read = notifs.filter(is_read=True).count()

    print("=" * 70)
    print("📊 ESTATÍSTICAS")
    print("=" * 70)
    print(f"📩 Não lidas: {unread}")
    print(f"✅ Lidas: {read}")
    print()

if __name__ == '__main__':
    list_notifications()

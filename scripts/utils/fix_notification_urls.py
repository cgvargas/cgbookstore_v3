"""
Script para corrigir URLs de notificações que usam ID para usar slug.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from accounts.models import ReadingNotification, SystemNotification


def fix_reading_notification_urls():
    """Corrige URLs em ReadingNotifications que usam ID para usar slug."""
    notifications = ReadingNotification.objects.filter(
        action_url__regex=r'/book/\d+/'
    )

    count = 0
    for notification in notifications:
        if notification.reading_progress and notification.reading_progress.book:
            book = notification.reading_progress.book
            # Atualizar URL para usar get_absolute_url()
            notification.action_url = book.get_absolute_url()
            notification.save()
            count += 1
            print(f"✓ Atualizada notificação {notification.id}: {notification.action_url}")

    print(f"\n✅ Total de ReadingNotifications atualizadas: {count}")
    return count


def fix_system_notification_urls():
    """Corrige URLs em SystemNotifications que usam ID para usar slug."""
    from core.models import Book

    notifications = SystemNotification.objects.filter(
        action_url__regex=r'/book/\d+/'
    )

    count = 0
    for notification in notifications:
        # Extrair book_id da extra_data ou da URL
        book_id = None
        if notification.extra_data and 'book_id' in notification.extra_data:
            book_id = notification.extra_data['book_id']
        else:
            # Tentar extrair da URL
            import re
            match = re.search(r'/book/(\d+)/', notification.action_url)
            if match:
                book_id = int(match.group(1))

        if book_id:
            try:
                book = Book.objects.get(id=book_id)
                notification.action_url = book.get_absolute_url()
                notification.save()
                count += 1
                print(f"✓ Atualizada notificação {notification.id}: {notification.action_url}")
            except Book.DoesNotExist:
                print(f"⚠ Livro {book_id} não encontrado para notificação {notification.id}")

    print(f"\n✅ Total de SystemNotifications atualizadas: {count}")
    return count


if __name__ == '__main__':
    print("=" * 60)
    print("CORRIGINDO URLs DE NOTIFICAÇÕES")
    print("=" * 60)
    print()

    print("1. Corrigindo ReadingNotifications...")
    reading_count = fix_reading_notification_urls()

    print("\n2. Corrigindo SystemNotifications...")
    system_count = fix_system_notification_urls()

    print("\n" + "=" * 60)
    print(f"✅ CONCLUÍDO! Total: {reading_count + system_count} notificações atualizadas")
    print("=" * 60)

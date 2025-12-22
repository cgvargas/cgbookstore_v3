"""
Teste da funcionalidade de mover automaticamente para "Lidos"
quando o usuário atinge a última página.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Book
from accounts.models import BookShelf, ReadingProgress

print("="*60)
print("TESTE: MOVER AUTOMATICAMENTE PARA LIDOS")
print("="*60)

# Buscar usuário e livro de teste
user = User.objects.get(username='claud')
book = Book.objects.filter(title__icontains='Curso Intensivo').first()

if not book:
    print("\nERRO: Livro de teste não encontrado")
    exit(1)

print(f"\nUsuario: {user.username}")
print(f"Livro: {book.title}")
print(f"Total de paginas: {book.page_count}")

# Buscar progresso
progress = ReadingProgress.objects.filter(user=user, book=book).first()

if not progress:
    print("\nERRO: ReadingProgress não encontrado")
    exit(1)

print(f"\nProgresso atual:")
print(f"  Pagina atual: {progress.current_page}")
print(f"  Total: {progress.total_pages}")
print(f"  Percentual: {progress.percentage}%")
print(f"  Finalizado: {progress.is_finished}")

# Verificar prateleira atual
current_shelves = BookShelf.objects.filter(user=user, book=book)
print(f"\nPrateleiras atuais:")
for shelf in current_shelves:
    print(f"  - {shelf.get_shelf_display()}")

# Atualizar para a última página
print(f"\n>>> Atualizando para a ultima pagina ({progress.total_pages})...")
progress.update_progress(progress.total_pages)

# Verificar se foi finalizado
print(f"\nApos update_progress:")
print(f"  Pagina atual: {progress.current_page}")
print(f"  Percentual: {progress.percentage}%")
print(f"  Finalizado: {progress.is_finished}")
print(f"  Data de conclusao: {progress.finished_at}")

# Verificar prateleiras após atualização
shelves_after = BookShelf.objects.filter(user=user, book=book)
print(f"\nPrateleiras DEPOIS da atualizacao:")
for shelf in shelves_after:
    print(f"  - {shelf.get_shelf_display()} (notas: {shelf.notes})")

# Verificar se está na prateleira "Lidos"
is_in_read = BookShelf.objects.filter(
    user=user,
    book=book,
    shelf_type='read'
).exists()

is_in_reading = BookShelf.objects.filter(
    user=user,
    book=book,
    shelf_type='reading'
).exists()

print("\n" + "="*60)
print("RESULTADO:")
print(f"  Livro em 'Lendo': {is_in_reading} (deve ser False)")
print(f"  Livro em 'Lidos': {is_in_read} (deve ser True)")
print("="*60)

if is_in_read and not is_in_reading:
    print("\nSUCESSO! Livro movido automaticamente para 'Lidos'")
else:
    print("\nFALHA! Livro NAO foi movido corretamente")

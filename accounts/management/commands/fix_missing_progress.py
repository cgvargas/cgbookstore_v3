from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import BookShelf, ReadingProgress
from core.models import Book


class Command(BaseCommand):
    help = 'Finds books on the "reading" shelf that are missing a ReadingProgress object and creates it.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando verificação de progressos de leitura ausentes ---'))

        # Encontra todas as entradas na prateleira "Lendo"
        shelves_to_fix = BookShelf.objects.filter(shelf_type='reading')

        if not shelves_to_fix.exists():
            self.stdout.write(
                self.style.WARNING('Nenhum livro encontrado na prateleira "Lendo". Nenhuma ação necessária.'))
            return

        self.stdout.write(f'Encontrados {shelves_to_fix.count()} livros na prateleira "Lendo". Verificando...')

        created_count = 0
        for shelf_entry in shelves_to_fix:
            user = shelf_entry.user
            book = shelf_entry.book

            # Verifica se já existe um progresso para este livro e usuário
            progress_exists = ReadingProgress.objects.filter(user=user, book=book).exists()

            if not progress_exists:
                # Se não existir, cria o objeto ReadingProgress
                ReadingProgress.objects.create(
                    user=user,
                    book=book,
                    total_pages=book.page_count or 1,
                    current_page=0
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Progresso criado para o livro "{book.title}" do usuário "{user.username}".'
                ))
            else:
                self.stdout.write(self.style.NOTICE(
                    f'Progresso para "{book.title}" de "{user.username}" já existe. Ignorando.'
                ))

        self.stdout.write(self.style.SUCCESS('--- Verificação concluída ---'))
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Total de {created_count} objetos de progresso ausentes foram criados.'))
        else:
            self.stdout.write(self.style.WARNING('Nenhum progresso ausente foi encontrado. Tudo certo!'))
"""
Management command para atualizar capas de livros usando Google Books API.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Book
from core.utils.google_books_api import update_book_cover_from_google
import time


class Command(BaseCommand):
    help = 'Atualiza capas dos livros usando Google Books API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Substituir capas existentes',
        )
        parser.add_argument(
            '--book-id',
            type=int,
            help='Atualizar apenas um livro específico pelo ID',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limitar número de livros a processar',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay em segundos entre requisições (padrão: 1.0)',
        )

    def handle(self, *args, **options):
        force = options['force']
        book_id = options['book_id']
        limit = options['limit']
        delay = options['delay']

        # Estatísticas
        total_books = 0
        success_count = 0
        failed_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS('Iniciando atualizacao de capas...'))
        self.stdout.write('')

        try:
            # Selecionar livros
            if book_id:
                books = Book.objects.filter(id=book_id)
                if not books.exists():
                    self.stdout.write(self.style.ERROR(f'Livro com ID {book_id} nao encontrado'))
                    return
            else:
                if force:
                    books = Book.objects.all()
                else:
                    books = Book.objects.filter(cover_image__isnull=True) | Book.objects.filter(cover_image='')

            if limit:
                books = books[:limit]

            total_books = books.count()

            if total_books == 0:
                self.stdout.write(self.style.WARNING('Nenhum livro para processar'))
                return

            self.stdout.write(f'Total de livros a processar: {total_books}')
            self.stdout.write('')

            # Processar livros
            for index, book in enumerate(books, start=1):
                self.stdout.write(f'[{index}/{total_books}] Processando: {book.title}')

                try:
                    success = update_book_cover_from_google(book, force=force)

                    if success:
                        success_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  Capa atualizada com sucesso')
                        )
                    else:
                        if book.cover_image and not force:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'  Livro ja tem capa (use --force para substituir)')
                            )
                        else:
                            failed_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'  Nao foi possivel encontrar capa')
                            )

                    # Delay entre requisições para não sobrecarregar a API
                    if index < total_books:
                        time.sleep(delay)

                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'  Erro: {str(e)}')
                    )

            # Resumo final
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('RESUMO DA ATUALIZACAO'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(f'Total processado: {total_books}')
            self.stdout.write(self.style.SUCCESS(f'Sucesso: {success_count}'))
            self.stdout.write(self.style.WARNING(f'Falhas: {failed_count}'))
            self.stdout.write(self.style.WARNING(f'Pulados: {skipped_count}'))

            # Cobertura
            total_books_db = Book.objects.count()
            books_with_cover = Book.objects.exclude(cover_image__isnull=True).exclude(cover_image='').count()
            coverage = (books_with_cover / total_books_db * 100) if total_books_db > 0 else 0

            self.stdout.write('')
            self.stdout.write(f'Cobertura total de capas: {books_with_cover}/{total_books_db} ({coverage:.1f}%)')
            self.stdout.write(self.style.SUCCESS('=' * 60))

        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Operacao cancelada pelo usuario'))
            self.stdout.write(f'Processados ate o momento: {success_count + failed_count + skipped_count}/{total_books}')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'Erro fatal: {str(e)}'))
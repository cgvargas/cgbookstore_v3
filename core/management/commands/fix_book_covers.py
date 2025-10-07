"""
Management command para corrigir capas de livros.
Remove referências a arquivos inexistentes e baixa novas capas.

Uso: python manage.py fix_book_covers
"""

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.models import Book
import requests
import os


class Command(BaseCommand):
    help = 'Corrige capas de livros (remove referências inválidas e baixa novas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--download',
            action='store_true',
            help='Baixa novas capas placeholder para livros sem capa',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('CORREÇÃO DE CAPAS DE LIVROS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # PASSO 1: Identificar livros com capas inválidas
        self.stdout.write('\n📋 PASSO 1: Verificando capas inválidas...')

        invalid_covers = 0
        valid_covers = 0
        no_cover = 0

        for book in Book.objects.all():
            if book.cover_image:
                # Verificar se arquivo existe
                if default_storage.exists(book.cover_image.name):
                    valid_covers += 1
                else:
                    invalid_covers += 1
                    self.stdout.write(
                        f'   ❌ {book.title[:40]:40} | '
                        f'Arquivo não existe: {book.cover_image.name}'
                    )
                    # Limpar referência inválida
                    book.cover_image = ''
                    book.save()
            else:
                no_cover += 1

        self.stdout.write(f'\n   ✓ Capas válidas: {valid_covers}')
        self.stdout.write(f'   ❌ Capas inválidas removidas: {invalid_covers}')
        self.stdout.write(f'   ⚠️  Sem capa: {no_cover + invalid_covers}')

        # PASSO 2: Baixar novas capas se solicitado
        if options['download']:
            self.stdout.write('\n📥 PASSO 2: Baixando capas placeholder...')

            books_without_cover = Book.objects.filter(cover_image='')
            total = books_without_cover.count()

            if total == 0:
                self.stdout.write('   ✓ Todos os livros já têm capa!')
            else:
                success = 0
                failed = 0

                for i, book in enumerate(books_without_cover, 1):
                    self.stdout.write(f'   [{i}/{total}] {book.title[:50]}...')

                    try:
                        # Usar Lorem Picsum com seed baseado no ID
                        seed = book.id
                        url = f'https://picsum.photos/seed/{seed}/400/600'

                        response = requests.get(url, timeout=10)

                        if response.status_code == 200:
                            # Nome do arquivo
                            filename = f'books/covers/{book.slug}.jpg'

                            # Salvar arquivo
                            path = default_storage.save(
                                filename,
                                ContentFile(response.content)
                            )

                            # Atualizar registro
                            book.cover_image = path
                            book.save()

                            success += 1
                            self.stdout.write(f'      ✓ Capa salva: {path}')
                        else:
                            failed += 1
                            self.stdout.write(
                                self.style.WARNING(f'      ⚠️  HTTP {response.status_code}')
                            )

                    except requests.exceptions.Timeout:
                        failed += 1
                        self.stdout.write(self.style.ERROR('      ❌ Timeout'))

                    except Exception as e:
                        failed += 1
                        self.stdout.write(self.style.ERROR(f'      ❌ Erro: {e}'))

                self.stdout.write(f'\n   ✓ Sucesso: {success}')
                self.stdout.write(f'   ❌ Falhas: {failed}')
        else:
            self.stdout.write('\n💡 Use --download para baixar capas placeholder')

        # PASSO 3: Relatório final
        self.stdout.write('\n📊 RELATÓRIO FINAL:')

        total_books = Book.objects.count()
        books_with_cover = Book.objects.exclude(cover_image='').count()
        books_without_cover = total_books - books_with_cover
        coverage = (books_with_cover / total_books * 100) if total_books > 0 else 0

        self.stdout.write(f'   Total de livros: {total_books}')
        self.stdout.write(f'   Com capa: {books_with_cover}')
        self.stdout.write(f'   Sem capa: {books_without_cover}')
        self.stdout.write(f'   Cobertura: {coverage:.1f}%')

        # Listar arquivos órfãos (na pasta mas sem registro no banco)
        self.stdout.write('\n🗑️  ARQUIVOS ÓRFÃOS:')

        media_files = set()
        if os.path.exists('media/books/covers'):
            for filename in os.listdir('media/books/covers'):
                media_files.add(f'books/covers/{filename}')

        db_files = set(Book.objects.exclude(cover_image='').values_list('cover_image', flat=True))

        orphan_files = media_files - db_files

        if orphan_files:
            self.stdout.write(f'   Encontrados {len(orphan_files)} arquivos órfãos:')
            for orphan in list(orphan_files)[:10]:
                self.stdout.write(f'      - {orphan}')
            if len(orphan_files) > 10:
                self.stdout.write(f'      ... e mais {len(orphan_files) - 10} arquivos')
        else:
            self.stdout.write('   ✓ Nenhum arquivo órfão')

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
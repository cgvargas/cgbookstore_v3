"""
Management command para baixar capas de livros via Google Books API.
Uso: python manage.py download_book_covers --author "Anne Rice"
"""

from django.core.management.base import BaseCommand, CommandError
from core.models import Book, Author
from core.utils.google_books_api import update_book_cover_from_google
import time


class Command(BaseCommand):
    help = 'Baixa capas de livros sem capa via Google Books API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--author',
            type=str,
            help='Nome do autor para filtrar livros'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força substituição de capas existentes'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Número máximo de livros a processar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula sem baixar capas'
        )

    def handle(self, *args, **options):
        author_name = options.get('author')
        force = options['force']
        limit = options['limit']
        dry_run = options['dry_run']

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.WARNING("  DOWNLOADER DE CAPAS - Google Books API"))
        self.stdout.write("=" * 70)

        if dry_run:
            self.stdout.write(self.style.NOTICE("\n🔍 MODO SIMULAÇÃO - Nenhum download será feito\n"))

        # Filtrar livros
        books = Book.objects.all()
        
        if author_name:
            author = Author.objects.filter(name__icontains=author_name).first()
            if not author:
                raise CommandError(f"Autor '{author_name}' não encontrado")
            books = books.filter(author=author)
            self.stdout.write(f"👤 Filtrando por autor: {author.name}")
        
        if not force:
            # Apenas livros sem capa
            books = books.filter(cover_image='')
            self.stdout.write(f"📚 Livros sem capa: {books.count()}")
        else:
            self.stdout.write(f"📚 Todos os livros (com ou sem capa): {books.count()}")
        
        books = books[:limit]
        
        if not books:
            self.stdout.write(self.style.SUCCESS("\n✅ Todos os livros já têm capas!"))
            return

        # Processar livros
        success = 0
        failed = 0
        skipped = 0

        for book in books:
            self.stdout.write(f"\n📖 Processando: {book.title}")
            
            if book.cover_image and not force:
                self.stdout.write(f"   ⏭️  Já tem capa")
                skipped += 1
                continue
            
            if dry_run:
                self.stdout.write(f"   📗 [SIMULAÇÃO] Buscaria capa no Google Books")
                success += 1
                continue
            
            try:
                result = update_book_cover_from_google(book, force=force)
                if result:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Capa baixada com sucesso!"))
                    success += 1
                else:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  Capa não encontrada"))
                    failed += 1
                
                # Delay para não sobrecarregar a API
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
                failed += 1

        # Resumo
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("  RESUMO"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"\n✅ Capas baixadas: {success}")
        self.stdout.write(f"⚠️  Não encontradas: {failed}")
        self.stdout.write(f"⏭️  Já tinham capa: {skipped}")
        
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                "\n⚠️  MODO SIMULAÇÃO - Execute sem --dry-run para baixar"
            ))

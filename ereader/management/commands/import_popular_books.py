"""
Comando para importar livros populares do Project Gutenberg.
Uso: python manage.py import_popular_books [--limit N] [--language LANG]
"""
from django.core.management.base import BaseCommand, CommandError
from ereader.models import EBook
from ereader.services.gutenberg import GutenbergService


class Command(BaseCommand):
    help = 'Importa livros populares do Project Gutenberg para a biblioteca'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Número máximo de livros a importar (padrão: 20)'
        )
        parser.add_argument(
            '--language',
            type=str,
            default='pt,en',
            help='Idiomas separados por vírgula (padrão: pt,en)'
        )
        parser.add_argument(
            '--portuguese-only',
            action='store_true',
            help='Importar apenas livros em português'
        )

    def handle(self, *args, **options):
        service = GutenbergService()
        limit = options['limit']
        
        self.stdout.write(
            self.style.NOTICE(f'🔍 Buscando livros populares (limite: {limit})...')
        )
        
        # Decidir qual método usar
        if options['portuguese_only']:
            self.stdout.write(self.style.NOTICE('📚 Buscando livros em português...'))
            books = service.get_portuguese_books(limit=limit)
        else:
            books = service.get_popular_books(limit=limit)
        
        if not books:
            raise CommandError('Nenhum livro encontrado na API do Gutenberg')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Encontrados {len(books)} livros')
        )
        
        imported_count = 0
        skipped_count = 0
        
        for book_data in books:
            external_id = book_data.get('external_id', '')
            title = book_data.get('title', 'Sem título')
            
            # Verificar se já existe
            if EBook.objects.filter(source='gutenberg', external_id=external_id).exists():
                self.stdout.write(f'   ⏩ Já existe: {title[:50]}')
                skipped_count += 1
                continue
            
            # Criar o livro
            try:
                ebook = EBook.objects.create(
                    title=title,
                    author=book_data.get('author', 'Autor desconhecido'),
                    description=book_data.get('description', ''),
                    cover_image=book_data.get('cover_image', ''),
                    epub_url=book_data.get('epub_url', ''),
                    source='gutenberg',
                    external_id=external_id,
                    language=book_data.get('language', 'en'),
                    subjects=book_data.get('subjects', []),
                    is_public_domain=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(f'   📖 Importado: {ebook.title[:50]}')
                )
                imported_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro ao importar "{title[:30]}": {e}')
                )
        
        # Resumo
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'📊 Resumo:'))
        self.stdout.write(self.style.SUCCESS(f'   • Importados: {imported_count}'))
        self.stdout.write(self.style.SUCCESS(f'   • Já existentes: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

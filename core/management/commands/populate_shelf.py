"""
Management command genérico para popular prateleiras via Google Books API.
Aceita parâmetros para especificar o arquivo markdown e nome da prateleira.
"""

import os
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from core.models import Section, SectionItem, Book, Author, Category
from core.utils.google_books_api import search_books, download_cover, parse_google_books_date


class Command(BaseCommand):
    help = 'Popula prateleiras com dados do Google Books a partir de arquivo markdown'

    def add_arguments(self, parser):
        parser.add_argument(
            'markdown_file',
            type=str,
            help='Nome do arquivo markdown (relativo ao BASE_DIR)'
        )
        parser.add_argument(
            'shelf_title',
            type=str,
            help='Título da prateleira a ser criada'
        )
        parser.add_argument(
            '--subtitle',
            type=str,
            default='',
            help='Subtítulo opcional da prateleira'
        )
        parser.add_argument(
            '--order',
            type=int,
            default=20,
            help='Ordem de exibição da prateleira (padrão: 20)'
        )

    def handle(self, *args, **options):
        markdown_file = options['markdown_file']
        shelf_title = options['shelf_title']
        subtitle = options['subtitle']
        order = options['order']

        self.stdout.write(self.style.SUCCESS(f'📚 INICIANDO IMPORTAÇÃO: {shelf_title}'))

        # 1. Verificar arquivo markdown
        file_path = os.path.join(settings.BASE_DIR, markdown_file)
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_path}'))
            return

        # 2. Ler livros do arquivo
        books_to_fetch = self.parse_markdown(file_path)

        if not books_to_fetch:
            self.stdout.write(self.style.WARNING('Nenhum livro encontrado no arquivo.'))
            return

        self.stdout.write(f'📖 Encontrados {len(books_to_fetch)} livros para importar.')

        # 3. Criar ou obter a Seção
        section, created = Section.objects.get_or_create(
            title=shelf_title,
            defaults={
                'subtitle': subtitle,
                'layout': 'carousel',
                'active': True,
                'order': order,
                'content_type': 'books',
                'show_price': False,
                'show_author': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Seção criada: {shelf_title}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'ℹ️ Seção existente: {shelf_title}'))

        # ContentType para SectionItem
        book_content_type = ContentType.objects.get_for_model(Book)

        # 4. Processar cada livro
        order_count = SectionItem.objects.filter(section=section).count() + 1
        imported_count = 0
        linked_count = 0

        for book_data in books_to_fetch:
            title_query = book_data['title']
            author_query = book_data['author']

            self.stdout.write(f'\n🔎 Buscando: "{title_query}" de {author_query}...')

            # Verificar se já existe no banco
            existing_book = Book.objects.filter(title__icontains=title_query).first()

            if existing_book:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Livro já existe: {existing_book.title}'))
                book = existing_book
            else:
                # Buscar na API e criar
                book = self.fetch_and_create_book(title_query, author_query)
                if not book:
                    continue
                imported_count += 1
                time.sleep(1)  # Rate limit

            # 5. Adicionar à Seção (se não estiver)
            if not SectionItem.objects.filter(
                section=section, 
                object_id=book.id, 
                content_type=book_content_type
            ).exists():
                SectionItem.objects.create(
                    section=section,
                    content_type=book_content_type,
                    object_id=book.id,
                    order=order_count
                )
                self.stdout.write(self.style.SUCCESS(f'  ➕ Adicionado à prateleira'))
                order_count += 1
                linked_count += 1
            else:
                self.stdout.write(f'  ℹ️ Já está na prateleira.')

        self.stdout.write(self.style.SUCCESS(
            f'\n✨ Concluído! Importados: {imported_count} | Vinculados: {linked_count}'
        ))

    def parse_markdown(self, file_path):
        """Lê o arquivo markdown e extrai lista de livros"""
        books = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Padrão: - Título — Autor
                if line.startswith('- ') and '—' in line:
                    parts = line[2:].split('—')
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        author = parts[1].strip()
                        books.append({'title': title, 'author': author})
        return books

    def fetch_and_create_book(self, title, author):
        """Busca no Google Books e salva no banco"""
        results = search_books(title=title, author=author, max_results=1)

        if not results or 'books' not in results or not results['books']:
            self.stdout.write(self.style.ERROR(f'  ❌ Não encontrado: {title}'))
            return None

        g_book = results['books'][0]

        # Criar/Obter Autor
        author_name = g_book['authors'][0] if g_book.get('authors') else author
        author_obj, _ = Author.objects.get_or_create(
            name=author_name,
            defaults={'slug': slugify(author_name)}
        )

        # Criar/Obter Categoria
        api_categories = g_book.get('categories', [])
        category_name = api_categories[0] if api_categories else 'Geral'
        category_obj, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'slug': slugify(category_name)}
        )

        try:
            # Verificar se já existe por google_books_id
            google_id = g_book.get('google_book_id')
            if google_id:
                existing = Book.objects.filter(google_books_id=google_id).first()
                if existing:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Google ID já existe: {existing.title}'))
                    return existing

            pub_date = parse_google_books_date(g_book.get('published_date'))

            book = Book.objects.create(
                title=g_book.get('title') or title,
                subtitle=g_book.get('subtitle'),
                author=author_obj,
                category=category_obj,
                description=g_book.get('description', ''),
                publication_date=pub_date,
                isbn=g_book.get('isbn_13') or g_book.get('isbn_10'),
                publisher=g_book.get('publisher') or '',
                google_books_id=google_id,
                page_count=g_book.get('page_count'),
                average_rating=g_book.get('average_rating'),
                ratings_count=g_book.get('ratings_count'),
                language=g_book.get('language', 'pt'),
                preview_link=g_book.get('preview_link'),
                info_link=g_book.get('info_link')
            )

            # Baixar capa
            if g_book.get('thumbnail'):
                self.stdout.write('  🖼️ Baixando capa...')
                cover_path = download_cover(g_book['thumbnail'], book.slug)
                if cover_path:
                    book.cover_image = cover_path
                    book.save()

            self.stdout.write(self.style.SUCCESS(f'  💾 Salvo: {book.title}'))
            return book

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Erro: {str(e)}'))
            return None

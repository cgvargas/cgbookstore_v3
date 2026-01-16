"""
Management command para popular prateleiras infantis via Google Books API.
Baseado no arquivo: novas_prateleiras_infantil_google_books.md
"""

import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from core.models import Section, SectionItem, Book, Author, Category
from core.utils.google_books_api import search_books, download_cover, parse_google_books_date
import time

class Command(BaseCommand):
    help = 'Popula prateleiras infantis com dados do Google Books'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('👶 INICIANDO IMPORTAÇÃO DE LIVROS INFANTIS'))
        
        # 1. Ler arquivo markdown
        file_path = os.path.join(settings.BASE_DIR, 'novas_prateleiras_infantil_google_books.md')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_path}'))
            return

        # Lista de livros para buscar (Titulo, Autor)
        # Extraindo do markdown manual para garantir precisão ou implementar parser
        # Vou implementar um parser simples baseado no formato conhecido
        books_to_fetch = self.parse_markdown(file_path)
        
        if not books_to_fetch:
            self.stdout.write(self.style.WARNING('Nenhum livro encontrado no arquivo.'))
            return

        self.stdout.write(f'📚 Encontrados {len(books_to_fetch)} livros para importar.')

        # 2. Criar ou obter a Seção
        section_title = "Infantil & Infantojuvenil – Sucessos Mundiais"
        section, created = Section.objects.get_or_create(
            title=section_title,
            defaults={
                'subtitle': 'Os maiores clássicos para crianças e jovens leitores',
                'layout': 'carousel', # Ou 'grid', conforme preferência
                'active': True,
                'order': 10, # Ordem arbitrária, pode ajustar
                'content_type': 'books',
                'show_price': False,
                'show_author': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Seção criada: {section_title}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'ℹ️ Seção existente encontrada: {section_title}'))

        # ContentType para SectionItem
        book_content_type = ContentType.objects.get_for_model(Book)

        # 3. Processar cada livro
        order_count = SectionItem.objects.filter(section=section).count() + 1
        
        for book_data in books_to_fetch:
            title_query = book_data['title']
            author_query = book_data['author']
            
            self.stdout.write(f'\n🔎 Buscando: "{title_query}" de {author_query}...')
            
            # Verificar se já existe no banco (evitar duplicação)
            # Busca aproximada
            existing_book = Book.objects.filter(
                title__icontains=title_query
            ).first()
             # Se for muito genérico, poderia adicionar author__name__icontains
            
            if existing_book:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Livro já existe no banco: {existing_book.title}'))
                book = existing_book
            else:
                # Buscar na API
                book = self.fetch_and_create_book(title_query, author_query)
                if not book:
                    continue
                time.sleep(1) # Rate limit prevent

            # 4. Adicionar à Seção
            if not SectionItem.objects.filter(section=section, object_id=book.id, content_type=book_content_type).exists():
                SectionItem.objects.create(
                    section=section,
                    content_type=book_content_type,
                    object_id=book.id,
                    order=order_count
                )
                self.stdout.write(self.style.SUCCESS(f'  ➕ Adicionado à prateleira "{section_title}"'))
                order_count += 1
            else:
                self.stdout.write(f'  ℹ️ Já está na prateleira.')

        self.stdout.write(self.style.SUCCESS('\n✨ Processo finalizado com sucesso!'))

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
                # Padrão para séries (ex: - Harry Potter (série)) - Ignorando por enquanto se não tiver autor explícito na linha ou tratar diferente
                # O prompt diz "Realizar busca pelo padrão: Título + Autor". 
                # As linhas de "Séries" no final do arquivo não tem autor explícito na mesma linha,
                # mas os livros individuais listados antes têm. Vou focar nos livros individuais listados.
        return books

    def fetch_and_create_book(self, title, author):
        """Busca no Google Books e salva no banco"""
        results = search_books(title=title, author=author, max_results=1)
        
        if not results or 'books' not in results or not results['books']:
            self.stdout.write(self.style.ERROR(f'  ❌ Não encontrado na API: {title}'))
            return None

        g_book = results['books'][0]
        
        # Validações básicas sugeridas no prompt
        if not g_book.get('description'):
            self.stdout.write(self.style.WARNING('  ⚠️ Sem descrição. Importando mesmo assim...'))
        
        # Criar/Obter Autor, Categoria
        author_name = g_book['authors'][0] if g_book.get('authors') else author
        author_obj, _ = Author.objects.get_or_create(name=author_name)

        # Categoria - Tentar mapear ou usar padrão Infantil
        # A API retorna categorias em lista strings
        api_categories = g_book.get('categories', [])
        category_name = api_categories[0] if api_categories else 'Infantil'
        
        # Simplificação: Usar uma categoria padrão "Infantil" se a da API for muito estranha ou longa,
        # mas tentar usar a da API primeiro.
        category_obj, _ = Category.objects.get_or_create(name=category_name)

        try:
            # Parse data publication
            pub_date = parse_google_books_date(g_book.get('published_date'))

            book = Book.objects.create(
                title=g_book.get('title') or title,
                subtitle=g_book.get('subtitle'),
                author=author_obj,
                category=category_obj,
                description=g_book.get('description', ''),
                publication_date=pub_date,
                isbn=g_book.get('isbn_13') or g_book.get('isbn_10'),
                publisher=g_book.get('publisher', ''),
                # page_count...
                google_books_id=g_book.get('google_book_id'),
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

            self.stdout.write(self.style.SUCCESS(f'  💾 Livro salvo: {book.title}'))
            return book

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Erro ao salvar livro: {str(e)}'))
            return None

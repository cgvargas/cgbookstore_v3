"""
Management command para popular seções da home automaticamente.
Uso: python manage.py populate_sections
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from core.models import Section, SectionItem, Book, Category


class Command(BaseCommand):
    help = 'Popula seções da home com livros existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa seções existentes antes de popular',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('POPULAR SEÇÕES DA HOME'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Limpar seções se solicitado
        if options['clear']:
            Section.objects.all().delete()
            self.stdout.write(self.style.WARNING('Seções anteriores removidas\n'))

        # ContentType para Book
        book_content_type = ContentType.objects.get_for_model(Book)

        # SEÇÃO 1: Lançamentos 2025 (livros mais recentes)
        section1, created = Section.objects.get_or_create(
            title='Lançamentos 2025',
            defaults={
                'subtitle': 'Os livros mais recentes do nosso catálogo',
                'layout': 'carousel',
                'active': True,
                'order': 1
            }
        )
        if created:
            # Adicionar 10 livros mais recentes
            latest_books = Book.objects.order_by('-created_at')[:10]
            for order, book in enumerate(latest_books, 1):
                SectionItem.objects.create(
                    section=section1,
                    content_type=book_content_type,
                    object_id=book.id,
                    order=order
                )
            self.stdout.write(self.style.SUCCESS(f'✓ Seção "{section1.title}" criada com {latest_books.count()} livros'))

        # SEÇÃO 2: Fantasia (livros da categoria Fantasia)
        try:
            fantasy_category = Category.objects.get(name='Fantasia')
            section2, created = Section.objects.get_or_create(
                title='Fantasia',
                defaults={
                    'subtitle': 'Explore mundos mágicos e aventuras épicas',
                    'layout': 'carousel',
                    'active': True,
                    'order': 2
                }
            )
            if created:
                fantasy_books = Book.objects.filter(category=fantasy_category).order_by('-average_rating')[:10]
                for order, book in enumerate(fantasy_books, 1):
                    SectionItem.objects.create(
                        section=section2,
                        content_type=book_content_type,
                        object_id=book.id,
                        order=order
                    )
                self.stdout.write(self.style.SUCCESS(f'✓ Seção "{section2.title}" criada com {fantasy_books.count()} livros'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ Categoria "Fantasia" não encontrada'))

        # SEÇÃO 3: Romance
        try:
            romance_category = Category.objects.get(name='Romance')
            section3, created = Section.objects.get_or_create(
                title='Romance',
                defaults={
                    'subtitle': 'Histórias emocionantes de amor e paixão',
                    'layout': 'carousel',
                    'active': True,
                    'order': 3
                }
            )
            if created:
                romance_books = Book.objects.filter(category=romance_category).order_by('-average_rating')[:10]
                for order, book in enumerate(romance_books, 1):
                    SectionItem.objects.create(
                        section=section3,
                        content_type=book_content_type,
                        object_id=book.id,
                        order=order
                    )
                self.stdout.write(self.style.SUCCESS(f'✓ Seção "{section3.title}" criada com {romance_books.count()} livros'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ Categoria "Romance" não encontrada'))

        # SEÇÃO 4: Mais Vendidos (livros com melhor avaliação)
        section4, created = Section.objects.get_or_create(
            title='Mais Vendidos',
            defaults={
                'subtitle': 'Os favoritos dos nossos leitores',
                'layout': 'grid',
                'active': True,
                'order': 4
            }
        )
        if created:
            bestsellers = Book.objects.filter(average_rating__isnull=False).order_by('-average_rating')[:12]
            for order, book in enumerate(bestsellers, 1):
                SectionItem.objects.create(
                    section=section4,
                    content_type=book_content_type,
                    object_id=book.id,
                    order=order
                )
            self.stdout.write(self.style.SUCCESS(f'✓ Seção "{section4.title}" criada com {bestsellers.count()} livros'))

        # SEÇÃO 5: Ficção Científica
        try:
            scifi_category = Category.objects.get(name='Ficção Científica')
            section5, created = Section.objects.get_or_create(
                title='Ficção Científica',
                defaults={
                    'subtitle': 'Viaje pelo universo e explore novas tecnologias',
                    'layout': 'carousel',
                    'active': True,
                    'order': 5
                }
            )
            if created:
                scifi_books = Book.objects.filter(category=scifi_category).order_by('-average_rating')[:10]
                for order, book in enumerate(scifi_books, 1):
                    SectionItem.objects.create(
                        section=section5,
                        content_type=book_content_type,
                        object_id=book.id,
                        order=order
                    )
                self.stdout.write(self.style.SUCCESS(f'✓ Seção "{section5.title}" criada com {scifi_books.count()} livros'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ Categoria "Ficção Científica" não encontrada'))

        # Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        total_sections = Section.objects.filter(active=True).count()
        total_items = SectionItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ {total_sections} seções ativas'))
        self.stdout.write(self.style.SUCCESS(f'✓ {total_items} livros nas seções'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
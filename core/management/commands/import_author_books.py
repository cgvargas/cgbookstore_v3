"""
Management command para importar livros de um autor específico.
Uso: python manage.py import_author_books --author "Anne Rice" --exclude "Interview with the Vampire"

Este comando é generalista e pode ser usado para qualquer autor.
Execução em produção: via Render Shell ou localmente com DATABASE_URL de produção.
"""

import json
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from core.models import Book, Author, Category


# =============================================================================
# DADOS DE ANNE RICE (podem ser movidos para arquivo JSON externo)
# =============================================================================
ANNE_RICE_DATA = {
    "author": {
        "name": "Anne Rice",
        "bio": "Anne Rice (1941-2021) foi uma escritora americana conhecida por seus romances góticos, de horror e ficção erótica. Nascida Howard Allen Frances O'Brien em Nova Orleans, Louisiana, ela é mais famosa por criar as Crônicas Vampirescas, uma série que redefiniu o gênero vampírico na literatura moderna. Rice também escreveu sob os pseudônimos A.N. Roquelaure (ficção erótica) e Anne Rampling.",
    },
    "exclude_titles": [
        "Interview with the Vampire",
        "Entrevista com o Vampiro"
    ],
    "series": [
        {
            "name": "The Vampire Chronicles",
            "category": "Terror",
            "books": [
                {"title": "The Vampire Lestat", "year": 1985, "order": 2},
                {"title": "The Queen of the Damned", "year": 1988, "order": 3},
                {"title": "The Tale of the Body Thief", "year": 1992, "order": 4},
                {"title": "Memnoch the Devil", "year": 1995, "order": 5},
                {"title": "The Vampire Armand", "year": 1998, "order": 6},
                {"title": "Merrick", "year": 2000, "order": 7},
                {"title": "Blood and Gold", "year": 2001, "order": 8},
                {"title": "Blackwood Farm", "year": 2002, "order": 9},
                {"title": "Blood Canticle", "year": 2003, "order": 10},
                {"title": "Prince Lestat", "year": 2014, "order": 11},
                {"title": "Prince Lestat and the Realms of Atlantis", "year": 2016, "order": 12},
                {"title": "Blood Communion: A Tale of Prince Lestat", "year": 2018, "order": 13}
            ]
        },
        {
            "name": "Lives of the Mayfair Witches",
            "category": "Terror",
            "books": [
                {"title": "The Witching Hour", "year": 1990, "order": 1},
                {"title": "Lasher", "year": 1993, "order": 2},
                {"title": "Taltos", "year": 1994, "order": 3}
            ]
        },
        {
            "name": "New Tales of the Vampires",
            "category": "Terror",
            "books": [
                {"title": "Pandora", "year": 1998, "order": 1},
                {"title": "Vittorio the Vampire", "year": 1999, "order": 2}
            ]
        },
        {
            "name": "The Sleeping Beauty Quartet",
            "category": "Romance",
            "pseudonym": "A.N. Roquelaure",
            "books": [
                {"title": "The Claiming of Sleeping Beauty", "year": 1983, "order": 1},
                {"title": "Beauty's Punishment", "year": 1984, "order": 2},
                {"title": "Beauty's Release", "year": 1985, "order": 3},
                {"title": "Beauty's Kingdom", "year": 2015, "order": 4}
            ]
        },
        {
            "name": "Christ the Lord",
            "category": "Ficção",
            "books": [
                {"title": "Christ the Lord: Out of Egypt", "year": 2005, "order": 1},
                {"title": "Christ the Lord: The Road to Cana", "year": 2008, "order": 2}
            ]
        },
        {
            "name": "Songs of the Seraphim",
            "category": "Fantasia",
            "books": [
                {
                    "title": "Angel Time",
                    "subtitle": "The Songs of the Seraphim, Book One",
                    "year": 2009,
                    "month": 10,
                    "day": 27,
                    "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 288,
                    "isbn": "9780307745392",
                    "price": 17.90,
                    "language": "en",
                    "cover_url": "https://books.google.com/books/content?id=E3g0DwAAQBAJ&printsec=frontcover&img=1&zoom=1",
                    "description": "Angel Time é o primeiro volume da série Songs of the Seraphim. A história acompanha Toby O'Dare, um assassino profissional assombrado por seu passado violento e por visões perturbadoras. Sua vida muda radicalmente quando ele encontra o serafim Malchiah, que lhe oferece uma chance de redenção e o conduz por uma jornada espiritual que atravessa o tempo, confrontando fé, pecado, identidade e salvação em cenários históricos e contemporâneos."
                },
                {
                    "title": "Of Love and Evil",
                    "subtitle": "The Songs of the Seraphim, Book Two",
                    "year": 2010,
                    "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 176,
                    "language": "en",
                    "description": "Segundo volume da série Songs of the Seraphim. Toby O'Dare, agora redimido, é novamente convocado pelo anjo Malchiah para uma missão na Itália renascentista, onde deve investigar um caso de possessão demoníaca."
                }
            ]
        },

        {
            "name": "The Wolf Gift Chronicles",
            "category": "Terror",
            "books": [
                {"title": "The Wolf Gift", "year": 2012, "order": 1},
                {"title": "The Wolves of Midwinter", "year": 2013, "order": 2}
            ]
        },
        {
            "name": "Ramses the Damned",
            "category": "Terror",
            "books": [
                {"title": "The Mummy, or Ramses the Damned", "year": 1989, "order": 1},
                {"title": "Ramses the Damned: The Passion of Cleopatra", "year": 2017, "order": 2},
                {"title": "Ramses the Damned: The Reign of Osiris", "year": 2022, "order": 3}
            ]
        }
    ],
    "standalone": {
        "category": "Ficção",
        "books": [
            {"title": "The Feast of All Saints", "year": 1979},
            {"title": "Cry to Heaven", "year": 1982},
            {"title": "Exit to Eden", "year": 1985, "pseudonym": "Anne Rampling"},
            {"title": "Belinda", "year": 1986, "pseudonym": "Anne Rampling"},
            {"title": "Servant of the Bones", "year": 1996},
            {"title": "Violin", "year": 1997}
        ]
    }
}


class Command(BaseCommand):
    help = 'Importa livros de um autor específico para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--author',
            type=str,
            default='Anne Rice',
            help='Nome do autor (padrão: Anne Rice)'
        )
        parser.add_argument(
            '--exclude',
            type=str,
            nargs='*',
            default=[],
            help='Títulos a excluir da importação'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a importação sem modificar o banco'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Categoria padrão para todos os livros'
        )

    def handle(self, *args, **options):
        author_name = options['author']
        exclude_titles = options['exclude']
        dry_run = options['dry_run']
        default_category = options['category']

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.WARNING(f"  IMPORTADOR DE LIVROS: {author_name}"))
        self.stdout.write("=" * 70)

        if dry_run:
            self.stdout.write(self.style.NOTICE("\n🔍 MODO SIMULAÇÃO - Nenhum dado será modificado\n"))

        # Por enquanto, apenas Anne Rice está implementada
        if author_name.lower() != 'anne rice':
            raise CommandError(
                f"Autor '{author_name}' não implementado. "
                f"Atualmente disponível: Anne Rice"
            )

        data = ANNE_RICE_DATA
        
        # Adicionar exclusões do usuário
        all_exclusions = data['exclude_titles'] + exclude_titles
        
        # Criar ou obter autor
        author = self._get_or_create_author(data['author'], dry_run)
        
        # Processar séries
        books_added = 0
        books_skipped = 0
        
        for series in data['series']:
            series_name = series['name']
            category_name = default_category or series['category']
            pseudonym = series.get('pseudonym', '')
            
            self.stdout.write(f"\n📚 Série: {series_name}")
            if pseudonym:
                self.stdout.write(f"   (Pseudônimo: {pseudonym})")
            
            category = self._get_or_create_category(category_name, dry_run)
            
            for book_data in series['books']:
                result = self._add_book(
                    book_data=book_data,
                    author=author,
                    category=category,
                    series_name=series_name,
                    pseudonym=pseudonym,
                    exclusions=all_exclusions,
                    dry_run=dry_run
                )
                if result == 'added':
                    books_added += 1
                elif result == 'skipped':
                    books_skipped += 1
        
        # Processar livros standalone
        standalone = data.get('standalone', {})
        if standalone:
            self.stdout.write(f"\n📖 Livros Avulsos (Standalone)")
            category_name = default_category or standalone['category']
            category = self._get_or_create_category(category_name, dry_run)
            
            for book_data in standalone['books']:
                pseudonym = book_data.get('pseudonym', '')
                result = self._add_book(
                    book_data=book_data,
                    author=author,
                    category=category,
                    series_name=None,
                    pseudonym=pseudonym,
                    exclusions=all_exclusions,
                    dry_run=dry_run
                )
                if result == 'added':
                    books_added += 1
                elif result == 'skipped':
                    books_skipped += 1
        
        # Resumo
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("  RESUMO DA IMPORTAÇÃO"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"\n✅ Livros adicionados: {books_added}")
        self.stdout.write(f"⏭️  Livros ignorados (já existem ou excluídos): {books_skipped}")
        
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                "\n⚠️  MODO SIMULAÇÃO - Execute sem --dry-run para aplicar alterações"
            ))
        else:
            # Verificação final
            total = Book.objects.filter(author=author).count()
            self.stdout.write(f"\n📊 Total de livros de {author_name} no banco: {total}")

    def _get_or_create_author(self, author_data, dry_run):
        """Cria ou obtém o autor."""
        name = author_data['name']
        
        if dry_run:
            author = Author.objects.filter(name=name).first()
            if author:
                self.stdout.write(f"👤 Autor existente: {name}")
            else:
                self.stdout.write(f"👤 [SIMULAÇÃO] Criar autor: {name}")
                author = Author(name=name)
            return author
        
        author, created = Author.objects.get_or_create(
            name=name,
            defaults={
                'bio': author_data.get('bio', ''),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"👤 Autor criado: {name}"))
        else:
            self.stdout.write(f"👤 Autor existente: {name}")
        
        return author

    def _get_or_create_category(self, category_name, dry_run):
        """Cria ou obtém a categoria."""
        if dry_run:
            category = Category.objects.filter(name=category_name).first()
            if not category:
                category = Category(name=category_name)
            return category
        
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'featured': False}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"   📁 Categoria criada: {category_name}"))
        
        return category

    def _add_book(self, book_data, author, category, series_name, pseudonym, exclusions, dry_run):
        """Adiciona um livro ao banco de dados com dados editoriais completos."""
        title = book_data['title']
        year = book_data['year']
        month = book_data.get('month', 1)
        day = book_data.get('day', 1)
        order = book_data.get('order', 0)
        
        # Campos editoriais opcionais
        subtitle = book_data.get('subtitle', '')
        publisher = book_data.get('publisher', '')
        pages = book_data.get('pages')
        isbn = book_data.get('isbn', '')
        price = book_data.get('price')
        language = book_data.get('language', 'en')
        cover_url = book_data.get('cover_url', '')
        custom_description = book_data.get('description', '')
        
        # Verificar exclusões
        title_lower = title.lower()
        for exclusion in exclusions:
            if exclusion.lower() in title_lower or title_lower in exclusion.lower():
                self.stdout.write(f"   ⛔ Excluído: {title}")
                return 'excluded'
        
        # Verificar se já existe
        existing = Book.objects.filter(title__iexact=title).first()
        if existing:
            self.stdout.write(f"   ⏭️  Já existe: {title}")
            return 'skipped'
        
        # Construir descrição (usar custom se disponível, senão gerar)
        if custom_description:
            description = custom_description
        else:
            description_parts = []
            if series_name:
                description_parts.append(f"Série: {series_name}")
                if order:
                    description_parts.append(f"Livro {order} da série")
            if pseudonym:
                description_parts.append(f"Publicado sob o pseudônimo {pseudonym}")
            description = ". ".join(description_parts) + "." if description_parts else ""
        
        if dry_run:
            extras = []
            if isbn:
                extras.append(f"ISBN: {isbn}")
            if pages:
                extras.append(f"{pages}p")
            if publisher:
                extras.append(publisher)
            extra_info = f" [{', '.join(extras)}]" if extras else ""
            self.stdout.write(f"   📗 [SIMULAÇÃO] Adicionar: {title} ({year}){extra_info}")
            return 'added'
        
        # Criar o livro com todos os campos disponíveis
        try:
            book = Book(
                title=title,
                subtitle=subtitle,
                author=author,
                category=category,
                description=description,
                publication_date=date(year, month, day),
                publisher=publisher,
                page_count=pages,
                isbn=isbn if isbn else None,
                price=price,
                language=language,
            )
            book.save()
            
            # Log detalhado
            extras = []
            if isbn:
                extras.append(f"ISBN: {isbn}")
            if pages:
                extras.append(f"{pages}p")
            if publisher:
                extras.append(publisher)
            extra_info = f" [{', '.join(extras)}]" if extras else ""
            
            self.stdout.write(self.style.SUCCESS(f"   ✅ Adicionado: {title} ({year}){extra_info}"))
            return 'added'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro ao adicionar {title}: {e}"))
            return 'error'


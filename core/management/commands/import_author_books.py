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
# DADOS COMPLETOS DE ANNE RICE (com informações editoriais)
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
                {
                    "title": "The Vampire Lestat",
                    "year": 1985, "month": 10, "day": 31, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 560,
                    "isbn": "978-0394534435",
                    "description": "Segundo volume das Crônicas Vampirescas. Lestat conta sua história desde sua juventude na França do século XVIII até se tornar uma estrela do rock nos anos 1980."
                },
                {
                    "title": "The Queen of the Damned",
                    "year": 1988, "order": 3,
                    "publisher": "Alfred A. Knopf",
                    "pages": 448,
                    "isbn": "978-0394558233",
                    "description": "Terceiro volume das Crônicas Vampirescas. A antiga rainha vampira Akasha desperta e ameaça destruir a humanidade."
                },
                {
                    "title": "The Tale of the Body Thief",
                    "year": 1992, "order": 4,
                    "publisher": "Alfred A. Knopf",
                    "pages": 430,
                    "isbn": "978-0679405283",
                    "description": "Quarto volume das Crônicas Vampirescas. Lestat troca de corpo com um humano e enfrenta as consequências."
                },
                {
                    "title": "Memnoch the Devil",
                    "year": 1995, "order": 5,
                    "publisher": "Alfred A. Knopf",
                    "pages": 354,
                    "isbn": "978-0679441018",
                    "description": "Quinto volume das Crônicas Vampirescas. Lestat é levado ao Céu e ao Inferno pelo próprio Diabo."
                },
                {
                    "title": "The Vampire Armand",
                    "year": 1998, "order": 6,
                    "publisher": "Alfred A. Knopf",
                    "pages": 387,
                    "isbn": "978-0679454472",
                    "description": "Sexto volume das Crônicas Vampirescas. A história de Armand desde a Veneza renascentista."
                },
                {
                    "title": "Merrick",
                    "year": 2000, "order": 7,
                    "publisher": "Alfred A. Knopf",
                    "pages": 307,
                    "isbn": "978-0679454489",
                    "description": "Sétimo volume das Crônicas Vampirescas. Crossover com a série Mayfair Witches."
                },
                {
                    "title": "Blood and Gold",
                    "year": 2001, "month": 10, "day": 16, "order": 8,
                    "publisher": "Alfred A. Knopf",
                    "pages": 480,
                    "isbn": "978-0679454496",
                    "description": "Oitavo volume das Crônicas Vampirescas. A história de Marius através dos séculos."
                },
                {
                    "title": "Blackwood Farm",
                    "year": 2002, "order": 9,
                    "publisher": "Alfred A. Knopf",
                    "pages": 544,
                    "isbn": "978-0375411991",
                    "description": "Nono volume das Crônicas Vampirescas. Quinn Blackwood narra sua transformação."
                },
                {
                    "title": "Blood Canticle",
                    "year": 2003, "order": 10,
                    "publisher": "Alfred A. Knopf",
                    "pages": 320,
                    "isbn": "978-0375412007",
                    "description": "Décimo volume das Crônicas Vampirescas. Conclusão da saga de Quinn e Lestat."
                },
                {
                    "title": "Prince Lestat",
                    "year": 2014, "month": 10, "day": 28, "order": 11,
                    "publisher": "Alfred A. Knopf",
                    "pages": 464,
                    "isbn": "978-0307962522",
                    "description": "Décimo primeiro volume das Crônicas Vampirescas. O retorno de Lestat como príncipe dos vampiros."
                },
                {
                    "title": "Prince Lestat and the Realms of Atlantis",
                    "year": 2016, "order": 12,
                    "publisher": "Alfred A. Knopf",
                    "pages": 480,
                    "isbn": "978-0385353793",
                    "description": "Décimo segundo volume das Crônicas Vampirescas. Lestat descobre as origens alienígenas dos vampiros."
                },
                {
                    "title": "Blood Communion: A Tale of Prince Lestat",
                    "year": 2018, "month": 10, "day": 2, "order": 13,
                    "publisher": "Alfred A. Knopf",
                    "pages": 288,
                    "isbn": "978-1524732646",
                    "description": "Décimo terceiro e último volume das Crônicas Vampirescas. Lestat consolida seu reinado."
                }
            ]
        },
        {
            "name": "Lives of the Mayfair Witches",
            "category": "Terror",
            "books": [
                {
                    "title": "The Witching Hour",
                    "year": 1990, "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 966,
                    "isbn": "978-0394587868",
                    "description": "Primeiro volume da trilogia Mayfair Witches. A saga de uma família de bruxas de Nova Orleans."
                },
                {
                    "title": "Lasher",
                    "year": 1993, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 592,
                    "isbn": "978-0679412953",
                    "description": "Segundo volume da trilogia Mayfair Witches. O espírito Lasher ganha forma física."
                },
                {
                    "title": "Taltos",
                    "year": 1994, "month": 9, "day": 19, "order": 3,
                    "publisher": "Alfred A. Knopf",
                    "pages": 467,
                    "isbn": "978-0679425731",
                    "description": "Terceiro volume da trilogia Mayfair Witches. A história da raça Taltos é revelada."
                }
            ]
        },
        {
            "name": "New Tales of the Vampires",
            "category": "Terror",
            "books": [
                {
                    "title": "Pandora",
                    "year": 1998, "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 353,
                    "isbn": "978-0375401598",
                    "description": "Primeiro volume de New Tales. A vampira Pandora conta sua origem no Império Romano."
                },
                {
                    "title": "Vittorio the Vampire",
                    "year": 1999, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 292,
                    "isbn": "978-0375401602",
                    "description": "Segundo volume de New Tales. Um jovem nobre da Toscana se torna vampiro."
                }
            ]
        },
        {
            "name": "The Sleeping Beauty Quartet",
            "category": "Romance",
            "pseudonym": "A.N. Roquelaure",
            "books": [
                {
                    "title": "The Claiming of Sleeping Beauty",
                    "year": 1983, "order": 1,
                    "publisher": "E.P. Dutton",
                    "pages": 253,
                    "isbn": "978-0525242192",
                    "description": "Primeiro volume do quarteto. Reinterpretação erótica do conto da Bela Adormecida. Publicado sob pseudônimo A.N. Roquelaure."
                },
                {
                    "title": "Beauty's Punishment",
                    "year": 1984, "order": 2,
                    "publisher": "E.P. Dutton",
                    "pages": 233,
                    "isbn": "978-0525242611",
                    "description": "Segundo volume do quarteto. Continuação da saga erótica da Bela. Publicado sob pseudônimo A.N. Roquelaure."
                },
                {
                    "title": "Beauty's Release",
                    "year": 1985, "month": 6, "order": 3,
                    "publisher": "Plume",
                    "pages": 238,
                    "isbn": "978-0452266636",
                    "description": "Terceiro volume do quarteto. Beauty é vendida ao Sultão. Publicado sob pseudônimo A.N. Roquelaure."
                },
                {
                    "title": "Beauty's Kingdom",
                    "year": 2015, "month": 4, "day": 21, "order": 4,
                    "publisher": "Viking",
                    "pages": 368,
                    "isbn": "978-0525427995",
                    "description": "Quarto volume do quarteto, lançado 30 anos depois. Beauty e Laurent assumem o reino. Publicado sob pseudônimo A.N. Roquelaure."
                }
            ]
        },
        {
            "name": "Christ the Lord",
            "category": "Ficção",
            "books": [
                {
                    "title": "Christ the Lord: Out of Egypt",
                    "year": 2005, "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 321,
                    "isbn": "978-0375412011",
                    "description": "Primeiro volume. Jesus aos sete anos narra sua jornada do Egito para Nazaré."
                },
                {
                    "title": "Christ the Lord: The Road to Cana",
                    "year": 2008, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 336,
                    "isbn": "978-1400043521",
                    "description": "Segundo volume. Jesus antes de seu ministério público, incluindo o milagre em Caná."
                }
            ]
        },
        {
            "name": "Songs of the Seraphim",
            "category": "Fantasia",
            "books": [
                {
                    "title": "Angel Time",
                    "subtitle": "The Songs of the Seraphim, Book One",
                    "year": 2009, "month": 10, "day": 27, "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 288,
                    "isbn": "978-0307745392",
                    "price": 17.90,
                    "description": "Angel Time é o primeiro volume da série Songs of the Seraphim. A história acompanha Toby O'Dare, um assassino profissional assombrado por seu passado violento e por visões perturbadoras. Sua vida muda radicalmente quando ele encontra o serafim Malchiah, que lhe oferece uma chance de redenção."
                },
                {
                    "title": "Of Love and Evil",
                    "subtitle": "The Songs of the Seraphim, Book Two",
                    "year": 2010, "month": 11, "day": 30, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 192,
                    "isbn": "978-1400043545",
                    "description": "Segundo volume da série Songs of the Seraphim. Toby O'Dare é novamente convocado pelo anjo Malchiah para uma missão na Itália renascentista."
                }
            ]
        },
        {
            "name": "The Wolf Gift Chronicles",
            "category": "Terror",
            "books": [
                {
                    "title": "The Wolf Gift",
                    "year": 2012, "month": 2, "order": 1,
                    "publisher": "Alfred A. Knopf",
                    "pages": 416,
                    "isbn": "978-0307595119",
                    "description": "Primeiro volume. Reuben Golding é atacado por uma criatura misteriosa e se transforma em homem-lobo."
                },
                {
                    "title": "The Wolves of Midwinter",
                    "year": 2013, "order": 2,
                    "publisher": "Alfred A. Knopf",
                    "pages": 400,
                    "isbn": "978-0385349963",
                    "description": "Segundo volume. Reuben prepara o primeiro Natal em Nideck Point enquanto enfrenta novos mistérios."
                }
            ]
        },
        {
            "name": "Ramses the Damned",
            "category": "Terror",
            "books": [
                {
                    "title": "The Mummy, or Ramses the Damned",
                    "year": 1989, "order": 1,
                    "publisher": "Ballantine Books",
                    "pages": 448,
                    "isbn": "978-0345360007",
                    "description": "Primeiro volume. Ramsés II, o faraó imortal, desperta na Londres eduardiana."
                },
                {
                    "title": "Ramses the Damned: The Passion of Cleopatra",
                    "year": 2017, "month": 11, "day": 21, "order": 2,
                    "publisher": "Anchor Books",
                    "pages": 416,
                    "isbn": "978-1101970324",
                    "description": "Segundo volume, coescrito com Christopher Rice. Cleópatra renasce no século XX."
                },
                {
                    "title": "Ramses the Damned: The Reign of Osiris",
                    "year": 2022, "month": 2, "day": 1, "order": 3,
                    "publisher": "Anchor Books",
                    "pages": 368,
                    "isbn": "978-1101970331",
                    "description": "Terceiro volume, coescrito com Christopher Rice. Ramsés enfrenta uma ameaça dos deuses egípcios."
                }
            ]
        }
    ],
    "standalone": {
        "category": "Ficção",
        "books": [
            {
                "title": "The Feast of All Saints",
                "year": 1979, "order": 0,
                "publisher": "Simon & Schuster",
                "pages": 571,
                "isbn": "978-0671247553",
                "description": "Romance histórico sobre os 'gens de couleur libres' (pessoas livres de cor) na Nova Orleans antebellum."
            },
            {
                "title": "Cry to Heaven",
                "year": 1982, "order": 0,
                "publisher": "Alfred A. Knopf",
                "pages": 534,
                "isbn": "978-0394523514",
                "description": "Romance histórico sobre os castrati na Itália do século XVIII."
            },
            {
                "title": "Exit to Eden",
                "year": 1985, "month": 5, "order": 0,
                "pseudonym": "Anne Rampling",
                "publisher": "Arbor House",
                "pages": 336,
                "isbn": "978-0877956099",
                "description": "Romance erótico sobre um resort BDSM. Publicado sob pseudônimo Anne Rampling."
            },
            {
                "title": "Belinda",
                "year": 1986, "order": 0,
                "pseudonym": "Anne Rampling",
                "publisher": "Arbor House",
                "pages": 439,
                "isbn": "978-0877958260",
                "description": "Romance sobre um artista e uma jovem misteriosa. Publicado sob pseudônimo Anne Rampling."
            },
            {
                "title": "Servant of the Bones",
                "year": 1996, "order": 0,
                "publisher": "Alfred A. Knopf",
                "pages": 387,
                "isbn": "978-0679433015",
                "description": "Romance sobrenatural sobre Azriel, um espírito da antiga Babilônia."
            },
            {
                "title": "Violin",
                "year": 1997, "month": 10, "day": 15, "order": 0,
                "publisher": "Alfred A. Knopf",
                "pages": 289,
                "isbn": "978-0679433026",
                "description": "Romance gótico sobre uma viúva assombrada por um violinista fantasma."
            }
        ]
    }
}


# =============================================================================
# DADOS COMPLETOS DE ANTOINE DE SAINT-EXUPÉRY
# =============================================================================
SAINT_EXUPERY_DATA = {
    "author": {
        "name": "Antoine de Saint-Exupéry",
        "bio": "Antoine de Saint-Exupéry (1900-1944) foi um escritor e aviador francês. Nascido em Lyon, tornou-se piloto comercial e militar, experiências que inspiraram sua obra literária. É mundialmente conhecido por 'O Pequeno Príncipe', uma das obras mais traduzidas da história. Desapareceu em 1944 durante uma missão de reconhecimento sobre o Mediterrâneo.",
    },
    "exclude_titles": [
        "O Pequeno Príncipe",  # Já existe no banco
    ],
    "series": [],
    "standalone": {
        "category": "Ficção",
        "books": [
            {
                "title": "The Little Prince",
                "year": 1943, "month": 4, "day": 6, "order": 0,
                "publisher": "Reynal & Hitchcock",
                "pages": 96,
                "isbn": "978-0156012195",
                "description": "Uma fábula poética sobre um piloto que cai no Saara e encontra um pequeno príncipe de outro planeta. Explora temas de amor, amizade e o sentido da vida."
            },
            {
                "title": "Night Flight",
                "year": 1931, "order": 0,
                "publisher": "Gallimard",
                "pages": 96,
                "isbn": "978-0156656054",
                "description": "Romance sobre os pilotos do correio aéreo na América do Sul nos anos 1930. A história segue Rivière e Fabien em uma tempestade noturna."
            },
            {
                "title": "Wind, Sand and Stars",
                "year": 1939, "order": 0,
                "publisher": "Reynal & Hitchcock",
                "pages": 240,
                "isbn": "978-0156027496",
                "description": "Memórias líricas das experiências de Saint-Exupéry como piloto. Ganhou o Grand Prix du Roman e o National Book Award."
            },
            {
                "title": "Flight to Arras",
                "year": 1942, "order": 0,
                "publisher": "Reynal & Hitchcock",
                "pages": 168,
                "isbn": "978-0547539607",
                "description": "Relato pessoal de uma missão de reconhecimento sobre a França ocupada em 1940, refletindo sobre guerra e patriotismo."
            },
            {
                "title": "Southern Mail",
                "year": 1929, "order": 0,
                "publisher": "Gallimard",
                "pages": 132,
                "isbn": "978-0156839013",
                "description": "Primeiro romance de Saint-Exupéry, baseado em suas experiências como piloto do correio aéreo sobre o Norte da África."
            },
            {
                "title": "Letter to a Hostage",
                "year": 1943, "order": 0,
                "publisher": "Brentano's",
                "pages": 72,
                "isbn": "978-2070256617",
                "description": "Carta aberta escrita durante o exílio nos EUA, dedicada ao amigo Léon Werth na França ocupada."
            },
            {
                "title": "The Wisdom of the Sands",
                "year": 1948, "order": 0,
                "publisher": "Gallimard",
                "pages": 480,
                "isbn": "978-2070407477",
                "description": "Obra filosófica póstuma. Meditações de um príncipe berbere sobre liderança, civilização e a condição humana."
            },
            {
                "title": "Airman's Odyssey",
                "year": 1984, "order": 0,
                "publisher": "Harcourt",
                "pages": 456,
                "isbn": "978-0156037334",
                "description": "Coletânea com Night Flight, Wind Sand and Stars e Flight to Arras. Essencial para entender a visão do autor."
            },
        ]
    }
}


# =============================================================================
# MAPEAMENTO DE AUTORES DISPONÍVEIS
# =============================================================================
AUTHORS_DATA_MAP = {
    "anne rice": ANNE_RICE_DATA,
    "saint-exupéry": SAINT_EXUPERY_DATA,
    "saint-exupery": SAINT_EXUPERY_DATA,
    "antoine de saint-exupéry": SAINT_EXUPERY_DATA,
    "antoine de saint-exupery": SAINT_EXUPERY_DATA,
    "exupery": SAINT_EXUPERY_DATA,
    "exupéry": SAINT_EXUPERY_DATA,
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

        # Buscar dados do autor no mapeamento
        data = None
        author_name_lower = author_name.lower()
        for key, author_data in AUTHORS_DATA_MAP.items():
            if key in author_name_lower or author_name_lower in key:
                data = author_data
                break
        
        if not data:
            available = ", ".join(set(d['author']['name'] for d in AUTHORS_DATA_MAP.values()))
            raise CommandError(
                f"Autor '{author_name}' não implementado. "
                f"Disponíveis: {available}"
            )

        
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

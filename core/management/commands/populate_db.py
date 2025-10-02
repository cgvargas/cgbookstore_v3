"""
Management command para popular o banco de dados com dados de exemplo.

Uso:
    python manage.py populate_db
    python manage.py populate_db --clear
    python manage.py populate_db --books=50 --verbose
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from decimal import Decimal
import random

from core.models import Category, Author, Book


class Command(BaseCommand):
    """
    Comando para popular o banco de dados com categorias, autores e livros.
    """

    help = 'Popula o banco de dados com dados de exemplo (categorias, autores, livros)'

    def add_arguments(self, parser):
        """Define argumentos aceitos pelo comando."""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todos os dados antes de popular',
        )

        parser.add_argument(
            '--books',
            type=int,
            default=50,
            help='Número de livros a criar (padrão: 50)',
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe mensagens detalhadas durante a execução',
        )

    def handle(self, *args, **options):
        """Método principal do comando."""
        clear = options['clear']
        num_books = options['books']
        verbose = options['verbose']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🚀 POPULATE DATABASE - CGBookStore v3'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Limpar dados se solicitado
        if clear:
            self._clear_database(verbose)

        # Popular dados
        with transaction.atomic():
            categories = self._create_categories(verbose)
            authors = self._create_authors(verbose)
            self._create_books(categories, authors, num_books, verbose)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Resumo final
        self._print_summary()

    def _clear_database(self, verbose):
        """Limpa todos os dados existentes."""
        self.stdout.write(self.style.WARNING('\n🗑️  LIMPANDO BANCO DE DADOS...'))

        book_count = Book.objects.count()
        author_count = Author.objects.count()
        category_count = Category.objects.count()

        Book.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()

        if verbose:
            self.stdout.write(f'   - {book_count} livros removidos')
            self.stdout.write(f'   - {author_count} autores removidos')
            self.stdout.write(f'   - {category_count} categorias removidas')

        self.stdout.write(self.style.SUCCESS('✅ Banco de dados limpo!\n'))

    def _create_categories(self, verbose):
        """Cria categorias."""
        self.stdout.write(self.style.WARNING('\n📚 CRIANDO CATEGORIAS...'))

        # Lista apenas com nomes (sem description)
        categories_names = [
            'Romance',
            'Ficção Científica',
            'Fantasia',
            'Terror',
            'Suspense/Thriller',
            'Biografia',
            'História',
            'Ciência',
            'Filosofia',
            'Autoajuda',
            'Tecnologia',
            'Negócios',
            'Design',
            'Poesia',
            'Infantojuvenil',
        ]

        categories = []
        for name in categories_names:
            category, created = Category.objects.get_or_create(
                name=name
            )
            categories.append(category)

            if verbose:
                status = '✨ Criada' if created else '♻️  Já existe'
                self.stdout.write(f'   {status}: {name}')

        self.stdout.write(self.style.SUCCESS(f'✅ {len(categories)} categorias processadas!\n'))
        return categories

    def _create_authors(self, verbose):
        """Cria autores."""
        self.stdout.write(self.style.WARNING('👤 CRIANDO AUTORES...'))

        authors_data = [
            {
                'name': 'Machado de Assis',
                'bio': 'Joaquim Maria Machado de Assis foi um escritor brasileiro, considerado por muitos críticos o maior nome da literatura brasileira. Escreveu romances, contos, crônicas, poesias e peças teatrais.',
                'website': 'http://www.machadodeassis.org.br/',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Clarice Lispector',
                'bio': 'Clarice Lispector foi uma escritora e jornalista nascida na Ucrânia e naturalizada brasileira. Autora de romances, contos e ensaios, é considerada uma das escritoras brasileiras mais importantes do século XX.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Paulo Coelho',
                'bio': 'Paulo Coelho é um romancista, dramaturgo e letrista brasileiro. É um dos escritores mais lidos do mundo, com mais de 320 milhões de livros vendidos em mais de 170 países.',
                'website': 'https://paulocoelho.com/',
                'twitter': '@paulocoelho',
                'instagram': '@paulocoelho',
            },
            {
                'name': 'J.K. Rowling',
                'bio': 'Joanne Rowling, mais conhecida como J.K. Rowling, é uma escritora, roteirista e produtora britânica, notória por escrever a série de livros Harry Potter.',
                'website': 'https://www.jkrowling.com/',
                'twitter': '@jk_rowling',
                'instagram': '',
            },
            {
                'name': 'George Orwell',
                'bio': 'Eric Arthur Blair, mais conhecido pelo pseudônimo George Orwell, foi um escritor, jornalista e ensaísta político inglês. Sua obra é marcada por uma inteligência perspicaz e bem-humorada.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Isaac Asimov',
                'bio': 'Isaac Asimov foi um escritor e bioquímico norte-americano, autor de obras de ficção científica e divulgação científica. É considerado um dos principais autores do gênero.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Agatha Christie',
                'bio': 'Agatha Mary Clarissa Christie foi uma escritora britânica que atuou como romancista, contista, dramaturga e poetisa. É a autora de mistério mais conhecida da história.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Stephen King',
                'bio': 'Stephen Edwin King é um escritor norte-americano de terror, ficção sobrenatural, suspense, ficção científica e fantasia. Seus livros já venderam mais de 400 milhões de cópias.',
                'website': 'https://stephenking.com/',
                'twitter': '@StephenKing',
                'instagram': '@stephenking',
            },
            {
                'name': 'Neil Gaiman',
                'bio': 'Neil Richard MacKinnon Gaiman é um autor britânico de contos, romances, banda desenhada, graphic novels, áudio theatre e filmes. Suas obras incluem Sandman, Deuses Americanos e Coraline.',
                'website': 'https://www.neilgaiman.com/',
                'twitter': '@neilhimself',
                'instagram': '@neilhimself',
            },
            {
                'name': 'Yuval Noah Harari',
                'bio': 'Yuval Noah Harari é um historiador, filósofo e escritor israelense. É professor da Universidade Hebraica de Jerusalém e autor dos best-sellers Sapiens e Homo Deus.',
                'website': 'https://www.ynharari.com/',
                'twitter': '@harari_yuval',
                'instagram': '@yuval_noah_harari',
            },
            {
                'name': 'Malcolm Gladwell',
                'bio': 'Malcolm Timothy Gladwell é um jornalista, escritor e sociólogo britânico. Autor de diversos best-sellers sobre psicologia social e comportamento humano.',
                'website': 'https://www.gladwell.com/',
                'twitter': '@Gladwell',
                'instagram': '',
            },
            {
                'name': 'Michelle Obama',
                'bio': 'Michelle LaVaughn Robinson Obama é uma advogada, escritora e ex-primeira-dama dos Estados Unidos. Seu livro "Minha História" foi um dos mais vendidos de 2018.',
                'website': '',
                'twitter': '@MichelleObama',
                'instagram': '@michelleobama',
            },
            {
                'name': 'Dan Brown',
                'bio': 'Daniel Gerhard Brown é um escritor norte-americano de thrillers. É mais conhecido por seu romance O Código Da Vinci, que se tornou um dos livros mais vendidos da história.',
                'website': 'https://danbrown.com/',
                'twitter': '@authordanbrown',
                'instagram': '@authordanbrown',
            },
            {
                'name': 'Chimamanda Ngozi Adichie',
                'bio': 'Chimamanda Ngozi Adichie é uma escritora nigeriana. Suas obrasabordam temas como identidade, raça, feminismo e a experiência africana contemporânea.',
                'website': '',
                'twitter': '',
                'instagram': '@chimamanda_adichie',
            },
            {
                'name': 'Haruki Murakami',
                'bio': 'Haruki Murakami é um escritor e tradutor japonês. Suas obras combinam elementos do realismo com o surrealismo e são conhecidas mundialmente.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Margaret Atwood',
                'bio': 'Margaret Eleanor Atwood é uma poetisa, romancista, crítica literária e ensaísta canadense. É mais conhecida por seus romances de ficção especulativa, incluindo O Conto da Aia.',
                'website': 'https://margaretatwood.ca/',
                'twitter': '@MargaretAtwood',
                'instagram': '@margaretatwood',
            },
            {
                'name': 'Gabriel García Márquez',
                'bio': 'Gabriel José de la Concordia García Márquez foi um escritor, jornalista e ativista político colombiano. Ganhador do Prêmio Nobel de Literatura em 1982.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'J.R.R. Tolkien',
                'bio': 'John Ronald Reuel Tolkien foi um escritor, professor universitário e filólogo britânico. Autor das obras O Hobbit, O Senhor dos Anéis e O Silmarillion.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Virginia Woolf',
                'bio': 'Adeline Virginia Woolf foi uma escritora, ensaísta e editora britânica, conhecida como uma das mais proeminentes figuras do modernismo literário do século XX.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Carl Sagan',
                'bio': 'Carl Edward Sagan foi um cientista, astrônomo, astrofísico, cosmólogo, escritor e divulgador científico norte-americano. Autor do best-seller Cosmos.',
                'website': '',
                'twitter': '',
                'instagram': '',
            },
            {
                'name': 'Brené Brown',
                'bio': 'Brené Brown é uma professora, autora e palestrante norte-americana. Suas pesquisas sobre vulnerabilidade, coragem, autenticidade e vergonha a tornaram mundialmente conhecida.',
                'website': 'https://brenebrown.com/',
                'twitter': '@BreneBrown',
                'instagram': '@brenebrown',
            },
            {
                'name': 'Robert C. Martin',
                'bio': 'Robert Cecil Martin, conhecido como Uncle Bob, é um engenheiro de software e autor americano. É conhecido por seu trabalho em padrões de design de software e desenvolvimento ágil.',
                'website': 'http://cleancoder.com/',
                'twitter': '@unclebobmartin',
                'instagram': '',
            },
        ]

        authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults={
                    'bio': author_data['bio'],
                    'website': author_data['website'],
                    'twitter': author_data['twitter'],
                    'instagram': author_data['instagram'],
                }
            )
            authors.append(author)

            if verbose:
                status = '✨ Criado' if created else '♻️  Já existe'
                self.stdout.write(f'   {status}: {author_data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'✅ {len(authors)} autores processados!\n'))
        return authors

    def _create_books(self, categories, authors, num_books, verbose):
        """Cria livros."""
        self.stdout.write(self.style.WARNING(f'📖 CRIANDO LIVROS...'))

        # Mapeamento de categorias por nome para facilitar
        cat_map = {cat.name: cat for cat in categories}

        # Mapeamento de autores por nome para facilitar
        auth_map = {auth.name: auth for auth in authors}

        books_data = [
            # LITERATURA BRASILEIRA
            {
                'title': 'Dom Casmurro',
                'author': 'Machado de Assis',
                'category': 'Romance',
                'description': 'Dom Casmurro é um romance escrito por Machado de Assis em 1899. A obra narra a história de Bentinho e Capitu, um dos casais mais famosos da literatura brasileira, e o ciúme que corrói seu relacionamento.',
                'price': Decimal('35.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788544001080',
            },
            {
                'title': 'A Hora da Estrela',
                'author': 'Clarice Lispector',
                'category': 'Romance',
                'description': 'Último romance de Clarice Lispector, conta a história de Macabéa, uma nordestina que vive no Rio de Janeiro. Uma reflexão profunda sobre a condição humana e a existência.',
                'price': Decimal('32.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530851',
            },
            {
                'title': 'O Alquimista',
                'author': 'Paulo Coelho',
                'category': 'Ficção',
                'description': 'A história de Santiago, um jovem pastor que viaja da Espanha ao Egito em busca de um tesouro. Uma fábula sobre seguir seus sonhos e encontrar seu destino.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.3'),
                'stock': random.randint(5, 50),
                'isbn': '9788573020687',
            },

            # HARRY POTTER
            {
                'title': 'Harry Potter e a Pedra Filosofal',
                'author': 'J.K. Rowling',
                'category': 'Fantasia',
                'description': 'Harry Potter descobre que é um bruxo no seu aniversário de 11 anos. Ele é convidado para estudar na Escola de Magia e Bruxaria de Hogwarts, onde vive aventuras incríveis.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.9'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530788',
            },
            {
                'title': 'Harry Potter e a Câmara Secreta',
                'author': 'J.K. Rowling',
                'category': 'Fantasia',
                'description': 'No segundo ano em Hogwarts, Harry enfrenta novos desafios quando mensagens misteriosas aparecem nas paredes anunciando que a Câmara Secreta foi aberta.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530795',
            },
            {
                'title': 'Harry Potter e o Prisioneiro de Azkaban',
                'author': 'J.K. Rowling',
                'category': 'Fantasia',
                'description': 'Harry descobre que Sirius Black, um perigoso prisioneiro de Azkaban, escapou e está atrás dele. Mas nem tudo é o que parece nesta aventura cheia de reviravoltas.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.9'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530801',
            },

            # FICÇÃO CIENTÍFICA / DISTOPIA
            {
                'title': '1984',
                'author': 'George Orwell',
                'category': 'Ficção Científica',
                'description': 'Em um futuro distópico, Winston Smith vive sob o regime totalitário do Grande Irmão. Uma crítica poderosa aos governos autoritários e à vigilância em massa.',
                'price': Decimal('44.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788535914849',
            },
            {
                'title': 'Fundação',
                'author': 'Isaac Asimov',
                'category': 'Ficção Científica',
                'description': 'Primeiro livro da série Fundação, uma obra-prima da ficção científica que explora a queda e ascensão de civilizações galácticas através da psicohistória.',
                'price': Decimal('52.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788576570646',
            },
            {
                'title': 'Eu, Robô',
                'author': 'Isaac Asimov',
                'category': 'Ficção Científica',
                'description': 'Coletânea de contos que explora as Três Leis da Robótica e suas implicações. Uma reflexão sobre inteligência artificial, ética e o futuro da humanidade.',
                'price': Decimal('46.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788576572008',
            },

            # MISTÉRIO / SUSPENSE
            {
                'title': 'Assassinato no Expresso do Oriente',
                'author': 'Agatha Christie',
                'category': 'Suspense/Thriller',
                'description': 'O detetive Hercule Poirot investiga um assassinato em um trem bloqueado pela neve. Todos os passageiros são suspeitos neste clássico do mistério.',
                'price': Decimal('38.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788595084728',
            },
            {
                'title': 'O Código Da Vinci',
                'author': 'Dan Brown',
                'category': 'Suspense/Thriller',
                'description': 'Robert Langdon investiga um assassinato no Louvre que o leva a uma série de pistas escondidas nas obras de Leonardo da Vinci, revelando um segredo milenar.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.4'),
                'stock': random.randint(5, 50),
                'isbn': '9788580411201',
            },

            # TERROR
            {
                'title': 'O Iluminado',
                'author': 'Stephen King',
                'category': 'Terror',
                'description': 'Jack Torrance aceita um emprego como zelador de inverno no Hotel Overlook, isolado nas montanhas. Mas o hotel esconde forças sobrenaturais que ameaçam sua família.',
                'price': Decimal('59.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788556510471',
            },
            {
                'title': 'It: A Coisa',
                'author': 'Stephen King',
                'category': 'Terror',
                'description': 'Na cidade de Derry, crianças desaparecem misteriosamente. Um grupo de amigos enfrenta uma entidade maligna que assume a forma dos medos mais profundos de suas vítimas.',
                'price': Decimal('79.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788581050164',
            },

            # FANTASIA
            {
                'title': 'Deuses Americanos',
                'author': 'Neil Gaiman',
                'category': 'Fantasia',
                'description': 'Shadow Moon descobre que os deuses antigos vivem entre os humanos na América moderna, e uma guerra está prestes a começar entre os velhos deuses e os novos.',
                'price': Decimal('64.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788551001974',
            },
            {
                'title': 'O Hobbit',
                'author': 'J.R.R. Tolkien',
                'category': 'Fantasia',
                'description': 'Bilbo Bolseiro, um hobbit pacato, é arrastado para uma aventura épica pelo mago Gandalf para ajudar um grupo de anões a recuperar seu tesouro de um dragão.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.9'),
                'stock': random.randint(5, 50),
                'isbn': '9788533613379',
            },
            {
                'title': 'A Sociedade do Anel',
                'author': 'J.R.R. Tolkien',
                'category': 'Fantasia',
                'description': 'Primeiro volume da trilogia O Senhor dos Anéis. Frodo Bolseiro herda um anel mágico e parte em uma jornada para destruí-lo antes que caia nas mãos erradas.',
                'price': Decimal('59.90'),
                'rating': Decimal('5.0'),
                'stock': random.randint(5, 50),
                'isbn': '9788533613386',
            },

            # NÃO-FICÇÃO / HISTÓRIA
            {
                'title': 'Sapiens: Uma Breve História da Humanidade',
                'author': 'Yuval Noah Harari',
                'category': 'História',
                'description': 'Uma narrativa fascinante sobre a evolução da humanidade, desde os primeiros humanos até a era moderna, explorando como nos tornamos a espécie dominante.',
                'price': Decimal('67.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788525432629',
            },
            {
                'title': 'Homo Deus: Uma Breve História do Amanhã',
                'author': 'Yuval Noah Harari',
                'category': 'Ciência',
                'description': 'Harari explora o futuro da humanidade e como a tecnologia pode transformar o Homo sapiens em Homo deus, com poderes antes atribuídos apenas aos deuses.',
                'price': Decimal('69.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788535928181',
            },
            {
                'title': '21 Lições para o Século 21',
                'author': 'Yuval Noah Harari',
                'category': 'Filosofia',
                'description': 'Harari examina os desafios urgentes do presente: terrorismo, fake news, liberdade, igualdade e o significado da vida na era da tecnologia.',
                'price': Decimal('64.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788535930405',
            },

            # DESENVOLVIMENTO PESSOAL
            {
                'title': 'A Coragem de Ser Imperfeito',
                'author': 'Brené Brown',
                'category': 'Autoajuda',
                'description': 'Brené Brown explora como abraçar nossas imperfeições pode nos levar a uma vida mais autêntica, corajosa e conectada.',
                'price': Decimal('44.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788543105420',
            },

            # BIOGRAFIA
            {
                'title': 'Minha História',
                'author': 'Michelle Obama',
                'category': 'Biografia',
                'description': 'A ex-primeira-dama dos Estados Unidos narra sua trajetória, desde a infância em Chicago até os anos na Casa Branca, com honestidade e eloquência.',
                'price': Decimal('59.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788542215366',
            },

            # PSICOLOGIA / SOCIOLOGIA
            {
                'title': 'Rápido e Devagar: Duas Formas de Pensar',
                'author': 'Malcolm Gladwell',
                'category': 'Ciência',
                'description': 'Malcolm Gladwell explora os dois sistemas que governam nossa mente: o rápido, intuitivo e emocional; e o devagar, deliberado e lógico.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788573028720',
            },

            # CIÊNCIA
            {
                'title': 'Cosmos',
                'author': 'Carl Sagan',
                'category': 'Ciência',
                'description': 'Uma jornada épica pelo universo, explorando o cosmos e nosso lugar nele. Uma obra-prima da divulgação científica.',
                'price': Decimal('69.90'),
                'rating': Decimal('4.9'),
                'stock': random.randint(5, 50),
                'isbn': '9788535928419',
            },

            # LITERATURA MUNDIAL
            {
                'title': 'Cem Anos de Solidão',
                'author': 'Gabriel García Márquez',
                'category': 'Romance',
                'description': 'A saga da família Buendía em Macondo, uma obra-prima do realismo mágico que narra cem anos de história através de sete gerações.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788501012180',
            },
            {
                'title': 'Kafka à Beira-Mar',
                'author': 'Haruki Murakami',
                'category': 'Romance',
                'description': 'A história de Kafka Tamura, um garoto de 15 anos que foge de casa, e Satoru Nakata, um homem que conversa com gatos. Duas jornadas paralelas e surreais.',
                'price': Decimal('59.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788556520050',
            },
            {
                'title': 'O Conto da Aia',
                'author': 'Margaret Atwood',
                'category': 'Ficção Científica',
                'description': 'Em uma sociedade distópica teocrática, as mulheres perderam todos os direitos. Offred é uma Aia, forçada a gerar filhos para a elite. Uma crítica poderosa ao fundamentalismo.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530783',
            },
            {
                'title': 'Americanah',
                'author': 'Chimamanda Ngozi Adichie',
                'category': 'Romance',
                'description': 'Ifemelu deixa a Nigéria para estudar nos Estados Unidos, onde descobre o significado de ser negra. Uma história sobre identidade, amor e pertencimento.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788535927771',
            },
            {
                'title': 'Mrs. Dalloway',
                'author': 'Virginia Woolf',
                'category': 'Romance',
                'description': 'Um dia na vida de Clarissa Dalloway, uma mulher da alta sociedade londrina. Um marco do modernismo literário com seu fluxo de consciência revolucionário.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.4'),
                'stock': random.randint(5, 50),
                'isbn': '9788582850275',
            },

            # TECNOLOGIA / PROGRAMAÇÃO
            {
                'title': 'Código Limpo: Habilidades Práticas do Agile Software',
                'author': 'Robert C. Martin',
                'category': 'Tecnologia',
                'description': 'Uncle Bob ensina como escrever código limpo, legível e manutenível. Um guia essencial para desenvolvedores que querem melhorar suas habilidades.',
                'price': Decimal('89.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788576082675',
            },
            {
                'title': 'Arquitetura Limpa: O Guia do Artesão para Estrutura e Design de Software',
                'author': 'Robert C. Martin',
                'category': 'Tecnologia',
                'description': 'Robert C. Martin apresenta princípios universais de arquitetura de software que se aplicam a todos os paradigmas de programação.',
                'price': Decimal('89.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788550804606',
            },

            # MAIS CLÁSSICOS
            {
                'title': 'Orgulho e Preconceito',
                'author': 'Virginia Woolf',
                'category': 'Romance',
                'description': 'A história de Elizabeth Bennet e Mr. Darcy, um dos romances mais amados de todos os tempos. Uma crítica social perspicaz sobre classe e casamento.',
                'price': Decimal('34.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788544001059',
            },
            {
                'title': 'A Revolução dos Bichos',
                'author': 'George Orwell',
                'category': 'Ficção',
                'description': 'Uma fábula satírica sobre totalitarismo. Os animais de uma fazenda se rebelam contra os humanos, mas logo descobrem que alguns são mais iguais que outros.',
                'price': Decimal('32.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788535914801',
            },
            {
                'title': 'Coraline',
                'author': 'Neil Gaiman',
                'category': 'Infantojuvenil',
                'description': 'Coraline descobre uma porta secreta em sua nova casa que leva a uma versão alternativa de seu mundo, onde seus "outros pais" querem mantê-la para sempre.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788551001912',
            },
            {
                'title': 'O Oceano no Fim do Caminho',
                'author': 'Neil Gaiman',
                'category': 'Fantasia',
                'description': 'Um homem retorna à sua cidade natal e lembra de eventos fantásticos de sua infância envolvendo uma família mágica e forças antigas e perigosas.',
                'price': Decimal('44.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788551001906',
            },
            {
                'title': 'Nada se Opõe à Noite',
                'author': 'Clarice Lispector',
                'category': 'Poesia',
                'description': 'Uma coletânea de contos que exploram a condição humana, a solidão e a busca por significado através da prosa poética única de Clarice.',
                'price': Decimal('36.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530868',
            },
            {
                'title': 'Memórias Póstumas de Brás Cubas',
                'author': 'Machado de Assis',
                'category': 'Romance',
                'description': 'Narrado por um defunto, este romance revolucionário quebra as convenções literárias e apresenta uma visão irônica e pessimista da sociedade brasileira.',
                'price': Decimal('38.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788544001097',
            },
            {
                'title': 'Quincas Borba',
                'author': 'Machado de Assis',
                'category': 'Romance',
                'description': 'A história de Rubião, um professor que herda a fortuna de Quincas Borba e é explorado pela sociedade carioca. Uma crítica mordaz à ambição e à hipocrisia.',
                'price': Decimal('36.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788544001103',
            },
            {
                'title': 'A Paixão Segundo G.H.',
                'author': 'Clarice Lispector',
                'category': 'Filosofia',
                'description': 'G.H., uma escultora, vive uma experiência transcendental após matar uma barata. Uma profunda reflexão filosófica sobre existência e identidade.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.4'),
                'stock': random.randint(5, 50),
                'isbn': '9788532530875',
            },
            {
                'title': 'O Zahir',
                'author': 'Paulo Coelho',
                'category': 'Romance',
                'description': 'Um escritor famoso busca sua esposa desaparecida e, nessa jornada, descobre mais sobre si mesmo e o significado do amor e da liberdade.',
                'price': Decimal('42.90'),
                'rating': Decimal('4.2'),
                'stock': random.randint(5, 50),
                'isbn': '9788573025354',
            },
            {
                'title': 'Onze Minutos',
                'author': 'Paulo Coelho',
                'category': 'Romance',
                'description': 'Maria, uma jovem brasileira, trabalha como prostituta em Genebra e busca entender o verdadeiro significado do amor e do sexo.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.1'),
                'stock': random.randint(5, 50),
                'isbn': '9788573022582',
            },
            {
                'title': 'O Senhor das Moscas',
                'author': 'George Orwell',
                'category': 'Ficção',
                'description': 'Um grupo de meninos britânicos fica preso em uma ilha deserta e tenta governar a si mesmos, com resultados desastrosos. Uma alegoria sobre civilização e selvageria.',
                'price': Decimal('37.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788535914825',
            },
            {
                'title': 'O Hobbit (Edição Ilustrada)',
                'author': 'J.R.R. Tolkien',
                'category': 'Infantojuvenil',
                'description': 'Edição especial ilustrada da aventura de Bilbo Bolseiro. Perfeita para apresentar o mundo da Terra-média às novas gerações.',
                'price': Decimal('89.90'),
                'rating': Decimal('5.0'),
                'stock': random.randint(5, 50),
                'isbn': '9788533613362',
            },
            {
                'title': 'A Menina que Roubava Livros',
                'author': 'Neil Gaiman',
                'category': 'História',
                'description': 'Durante a Segunda Guerra Mundial na Alemanha, Liesel rouba livros e os compartilha com outros. Uma história comovente narrada pela Morte.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.8'),
                'stock': random.randint(5, 50),
                'isbn': '9788551001929',
            },
            {
                'title': 'Neuromancer',
                'author': 'Isaac Asimov',
                'category': 'Ficção Científica',
                'description': 'Case, um hacker, é contratado para o último trabalho de sua vida: invadir uma inteligência artificial. Um marco do gênero cyberpunk.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788576572015',
            },
            {
                'title': 'Morte no Nilo',
                'author': 'Agatha Christie',
                'category': 'Suspense/Thriller',
                'description': 'Hercule Poirot investiga um assassinato durante um cruzeiro pelo Nilo. Paixão, ciúme e vingança se entrelaçam neste clássico do mistério.',
                'price': Decimal('39.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788595084735',
            },
            {
                'title': 'Anjos e Demônios',
                'author': 'Dan Brown',
                'category': 'Suspense/Thriller',
                'description': 'Robert Langdon investiga o assassinato de um cientista do CERN e descobre uma conspiração dos Illuminati que ameaça o Vaticano.',
                'price': Decimal('52.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788580411218',
            },
            {
                'title': 'Carrie, A Estranha',
                'author': 'Stephen King',
                'category': 'Terror',
                'description': 'Carrie White é uma adolescente tímida com poderes telecinéticos. Quando é humilhada no baile de formatura, sua vingança será aterradora.',
                'price': Decimal('44.90'),
                'rating': Decimal('4.4'),
                'stock': random.randint(5, 50),
                'isbn': '9788581050171',
            },
            {
                'title': 'O Cemitério',
                'author': 'Stephen King',
                'category': 'Terror',
                'description': 'Louis Creed descobre um antigo cemitério indígena perto de sua casa que tem o poder de ressuscitar os mortos. Mas o que volta nunca é o mesmo.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788581050188',
            },
            {
                'title': 'Norwegian Wood',
                'author': 'Haruki Murakami',
                'category': 'Romance',
                'description': 'Toru Watanabe relembra seu romance com Naoko, uma jovem frágil e melancólica, durante os turbulentos anos 1960 no Japão.',
                'price': Decimal('54.90'),
                'rating': Decimal('4.5'),
                'stock': random.randint(5, 50),
                'isbn': '9788556520067',
            },
            {
                'title': 'Meio Sol Amarelo',
                'author': 'Chimamanda Ngozi Adichie',
                'category': 'História',
                'description': 'Ambientado durante a guerra civil nigeriana, o romance segue três personagens cujas vidas são transformadas pelo conflito.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.7'),
                'stock': random.randint(5, 50),
                'isbn': '9788535927764',
            },
            {
                'title': 'A Insustentável Leveza do Ser',
                'author': 'Virginia Woolf',
                'category': 'Filosofia',
                'description': 'Ambientado durante a Primavera de Praga, o romance explora o amor, a política e a filosofia através da vida de Tomás, Tereza, Sabina e Franz.',
                'price': Decimal('49.90'),
                'rating': Decimal('4.6'),
                'stock': random.randint(5, 50),
                'isbn': '9788582850282',
            },
        ]

        # Limitar ao número de livros solicitado pelo usuário
        books_data = books_data[:num_books]

        # Contadores para estatísticas
        books_created = 0
        books_skipped = 0

        # Loop para criar cada livro
        for book_data in books_data:
            # Buscar categoria e autor pelos nomes
            category = cat_map.get(book_data['category'])
            author = auth_map.get(book_data['author'])

            # Validar se categoria e autor existem
            if not category or not author:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'   ⚠️  Pulado: {book_data["title"]} (categoria ou autor não encontrado)'
                        )
                    )
                books_skipped += 1
                continue

            # Criar ou buscar livro existente
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'author': author,
                    'category': category,
                    'description': book_data['description'],
                    'price': book_data['price'],
                    'average_rating': book_data.get('rating'),  # rating → average_rating
                    'isbn': book_data.get('isbn'),
                    'publication_date': '2020-01-01',  # Data padrão
                    'publisher': 'Editora Padrão',
                }
            )

            # Atualizar contadores e exibir mensagem
            if created:
                books_created += 1
                if verbose:
                    self.stdout.write(
                        f'   ✨ Criado: {book_data["title"]} - R$ {book_data["price"]}'
                    )
            else:
                books_skipped += 1
                if verbose:
                    self.stdout.write(
                        f'   ♻️  Já existe: {book_data["title"]}'
                    )

        # Mensagem final com resumo
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {books_created} livros criados! ({books_skipped} já existiam)\n'
            )
        )

    def _print_summary(self):
        """Exibe resumo final."""
        self.stdout.write('\n📊 RESUMO FINAL:')
        self.stdout.write(f'   📚 Categorias: {Category.objects.count()}')
        self.stdout.write(f'   👤 Autores: {Author.objects.count()}')
        self.stdout.write(f'   📖 Livros: {Book.objects.count()}')
        self.stdout.write('')
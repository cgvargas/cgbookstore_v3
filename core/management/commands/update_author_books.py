"""
Management command para ATUALIZAR livros existentes de um autor com dados completos.
Uso: python manage.py update_author_books --author "Anne Rice"

Este comando atualiza livros já existentes com:
- ISBN-13
- Editora
- Número de páginas
- Descrição completa
- Capa (via Google Books API)
"""

import time
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from core.models import Book, Author
from core.utils.google_books_api import update_book_cover_from_google


# =============================================================================
# DADOS COMPLETOS PARA ATUALIZAÇÃO - ANNE RICE
# =============================================================================
ANNE_RICE_BOOKS_DATA = {
    # The Vampire Chronicles
    "The Vampire Lestat": {
        "isbn": "978-0394534435",
        "publisher": "Alfred A. Knopf",
        "pages": 560,
        "description": "Segundo volume das Crônicas Vampirescas. Lestat conta sua história desde sua juventude na França do século XVIII até se tornar uma estrela do rock nos anos 1980. Um épico vampírico que redefine o gênero."
    },
    "The Queen of the Damned": {
        "isbn": "978-0394558233",
        "publisher": "Alfred A. Knopf",
        "pages": 448,
        "description": "Terceiro volume das Crônicas Vampirescas. A antiga rainha vampira Akasha desperta após milênios de sono e ameaça destruir a humanidade. Os vampiros mais antigos devem se unir para impedi-la."
    },
    "The Tale of the Body Thief": {
        "isbn": "978-0679405283",
        "publisher": "Alfred A. Knopf",
        "pages": 430,
        "description": "Quarto volume das Crônicas Vampirescas. Lestat, cansado de sua existência imortal, aceita trocar de corpo com um humano. Mas quando o ladrão de corpos foge com seu corpo vampírico, ele precisa desesperadamente recuperá-lo."
    },
    "Memnoch the Devil": {
        "isbn": "978-0679441018",
        "publisher": "Alfred A. Knopf",
        "pages": 354,
        "description": "Quinto volume das Crônicas Vampirescas. Lestat é levado ao Céu e ao Inferno pelo próprio Diabo, que lhe mostra a verdadeira história da Criação e tenta recrutá-lo para uma missão extraordinária."
    },
    "The Vampire Armand": {
        "isbn": "978-0679454472",
        "publisher": "Alfred A. Knopf",
        "pages": 387,
        "description": "Sexto volume das Crônicas Vampirescas. Armand revela sua história desde a Veneza renascentista, onde foi transformado em vampiro por Marius, até os tempos modernos."
    },
    "Merrick": {
        "isbn": "978-0679454489",
        "publisher": "Alfred A. Knopf",
        "pages": 307,
        "description": "Sétimo volume das Crônicas Vampirescas. Crossover com a série Mayfair Witches. Louis busca a ajuda da bruxa Merrick para invocar o fantasma de Claudia."
    },
    "Blood and Gold": {
        "isbn": "978-0679454496",
        "publisher": "Alfred A. Knopf",
        "pages": 480,
        "description": "Oitavo volume das Crônicas Vampirescas. Marius, o vampiro romano, conta sua épica jornada de dois mil anos, desde a Roma antiga até o presente."
    },
    "Blackwood Farm": {
        "isbn": "978-0375411991",
        "publisher": "Alfred A. Knopf",
        "pages": 544,
        "description": "Nono volume das Crônicas Vampirescas. Quinn Blackwood, jovem herdeiro de uma plantação da Louisiana, narra sua transformação em vampiro e sua luta contra o fantasma que o assombra."
    },
    "Blood Canticle": {
        "isbn": "978-0375412007",
        "publisher": "Alfred A. Knopf",
        "pages": 320,
        "description": "Décimo volume das Crônicas Vampirescas. Conclusão da saga de Quinn Blackwood e Lestat, entrelaçada com a história das Bruxas Mayfair."
    },
    "Prince Lestat": {
        "isbn": "978-0307962522",
        "publisher": "Alfred A. Knopf",
        "pages": 464,
        "description": "Décimo primeiro volume das Crônicas Vampirescas. Lestat retorna como o príncipe dos vampiros, confrontando uma misteriosa Voz que está causando destruição entre os imortais."
    },
    "Prince Lestat and the Realms of Atlantis": {
        "isbn": "978-0385353793",
        "publisher": "Alfred A. Knopf",
        "pages": 480,
        "description": "Décimo segundo volume das Crônicas Vampirescas. Lestat descobre as origens alienígenas de Amel, o espírito que criou os vampiros, e os mistérios da perdida Atlântida."
    },
    "Blood Communion: A Tale of Prince Lestat": {
        "isbn": "978-1524732646",
        "publisher": "Alfred A. Knopf",
        "pages": 288,
        "description": "Décimo terceiro e último volume das Crônicas Vampirescas. Lestat consolida seu reinado como príncipe dos vampiros em meio a intrigas e novos desafios."
    },
    
    # Interview with the Vampire (caso exista sem dados)
    "Interview with the Vampire": {
        "isbn": "978-0394498201",
        "publisher": "Alfred A. Knopf",
        "pages": 340,
        "description": "Primeiro volume das Crônicas Vampirescas. Louis, um vampiro melancólico, conta sua história a um repórter em São Francisco, revelando sua transformação, sua relação com Lestat e a criação da vampira-criança Claudia."
    },
    
    # Lives of the Mayfair Witches
    "The Witching Hour": {
        "isbn": "978-0394587868",
        "publisher": "Alfred A. Knopf",
        "pages": 966,
        "description": "Primeiro volume da trilogia Mayfair Witches. A saga épica de uma família de bruxas de Nova Orleans através de séculos, focando em Rowan Mayfair e o espírito Lasher que a assombra."
    },
    "Lasher": {
        "isbn": "978-0679412953",
        "publisher": "Alfred A. Knopf",
        "pages": 592,
        "description": "Segundo volume da trilogia Mayfair Witches. O espírito Lasher finalmente ganha forma física, desencadeando consequências terríveis para a família Mayfair."
    },
    "Taltos": {
        "isbn": "978-0679425731",
        "publisher": "Alfred A. Knopf",
        "pages": 467,
        "description": "Terceiro volume da trilogia Mayfair Witches. A história da antiga raça Taltos é revelada através de Ashlar, um ser milenar que está ligado aos Mayfair."
    },
    
    # New Tales of the Vampires
    "Pandora": {
        "isbn": "978-0375401598",
        "publisher": "Alfred A. Knopf",
        "pages": 353,
        "description": "Primeiro volume de New Tales of the Vampires. A vampira Pandora conta sua origem no Império Romano e seu amor eterno pelo vampiro Marius."
    },
    "Vittorio the Vampire": {
        "isbn": "978-0375401602",
        "publisher": "Alfred A. Knopf",
        "pages": 292,
        "description": "Segundo volume de New Tales of the Vampires. Um jovem nobre da Toscana renascentista se torna vampiro após a destruição de sua família por uma corte de demônios."
    },
    
    # The Sleeping Beauty Quartet
    "The Claiming of Sleeping Beauty": {
        "isbn": "978-0525242192",
        "publisher": "E.P. Dutton",
        "pages": 253,
        "description": "Primeiro volume do quarteto Sleeping Beauty. Reinterpretação erótica do conto da Bela Adormecida, onde a princesa desperta para um mundo de prazer e submissão. Publicado sob pseudônimo A.N. Roquelaure."
    },
    "Beauty's Punishment": {
        "isbn": "978-0525242611",
        "publisher": "E.P. Dutton",
        "pages": 233,
        "description": "Segundo volume do quarteto Sleeping Beauty. Beauty é enviada à vila como punição, onde experimenta novos desafios e prazeres. Publicado sob pseudônimo A.N. Roquelaure."
    },
    "Beauty's Release": {
        "isbn": "978-0452266636",
        "publisher": "Plume",
        "pages": 238,
        "description": "Terceiro volume do quarteto Sleeping Beauty. Beauty é vendida ao Sultão e levada a um palácio exótico no Oriente. Publicado sob pseudônimo A.N. Roquelaure."
    },
    "Beauty's Kingdom": {
        "isbn": "978-0525427995",
        "publisher": "Viking",
        "pages": 368,
        "description": "Quarto volume do quarteto, lançado 30 anos após o terceiro. Beauty e Laurent assumem o reino e instituem novas tradições. Publicado sob pseudônimo A.N. Roquelaure."
    },
    
    # Christ the Lord
    "Christ the Lord: Out of Egypt": {
        "isbn": "978-0375412011",
        "publisher": "Alfred A. Knopf",
        "pages": 321,
        "description": "Primeiro volume da série Christ the Lord. Jesus aos sete anos narra sua jornada do Egito para Nazaré, descobrindo gradualmente sua natureza divina."
    },
    "Christ the Lord: The Road to Cana": {
        "isbn": "978-1400043521",
        "publisher": "Alfred A. Knopf",
        "pages": 336,
        "description": "Segundo volume da série Christ the Lord. Jesus antes de seu ministério público, vivendo em Nazaré e realizando o milagre em Caná."
    },
    
    # Songs of the Seraphim
    "Angel Time": {
        "isbn": "978-0307745392",
        "publisher": "Alfred A. Knopf",
        "pages": 288,
        "description": "Primeiro volume da série Songs of the Seraphim. Toby O'Dare, um assassino profissional assombrado por seu passado, encontra o serafim Malchiah que lhe oferece uma chance de redenção através de viagens no tempo."
    },
    "Of Love and Evil": {
        "isbn": "978-1400043545",
        "publisher": "Alfred A. Knopf",
        "pages": 192,
        "description": "Segundo volume da série Songs of the Seraphim. Toby O'Dare é novamente convocado pelo anjo Malchiah para uma missão na Itália renascentista, investigando um caso de possessão demoníaca."
    },
    
    # The Wolf Gift Chronicles
    "The Wolf Gift": {
        "isbn": "978-0307595119",
        "publisher": "Alfred A. Knopf",
        "pages": 416,
        "description": "Primeiro volume das Wolf Gift Chronicles. Reuben Golding, jovem jornalista de São Francisco, é atacado por uma criatura misteriosa e se transforma em homem-lobo, descobrindo um novo mundo sobrenatural."
    },
    "The Wolves of Midwinter": {
        "isbn": "978-0385349963",
        "publisher": "Alfred A. Knopf",
        "pages": 400,
        "description": "Segundo volume das Wolf Gift Chronicles. Reuben prepara o primeiro Natal em Nideck Point enquanto enfrenta novos mistérios e a chegada de outros morfos."
    },
    
    # Ramses the Damned
    "The Mummy, or Ramses the Damned": {
        "isbn": "978-0345360007",
        "publisher": "Ballantine Books",
        "pages": 448,
        "description": "Primeiro volume da série Ramses. O faraó Ramsés II, tornado imortal pelo elixir da vida, desperta na Londres eduardiana e se apaixona por Julie Stratford."
    },
    "Ramses the Damned: The Passion of Cleopatra": {
        "isbn": "978-1101970324",
        "publisher": "Anchor Books",
        "pages": 416,
        "description": "Segundo volume, coescrito com Christopher Rice. Cleópatra, ressuscitada no primeiro livro, busca sua própria identidade no século XX enquanto Ramsés enfrenta novas ameaças."
    },
    "Ramses the Damned: The Reign of Osiris": {
        "isbn": "978-1101970331",
        "publisher": "Anchor Books",
        "pages": 368,
        "description": "Terceiro volume, coescrito com Christopher Rice. Ramsés e seus aliados enfrentam uma ameaça dos deuses egípcios que ameaça o equilíbrio do mundo."
    },
    
    # Standalone
    "The Feast of All Saints": {
        "isbn": "978-0671247553",
        "publisher": "Simon & Schuster",
        "pages": 571,
        "description": "Romance histórico épico sobre os 'gens de couleur libres' (pessoas livres de cor) na Nova Orleans antebellum, explorando suas vidas, amores e as tensões raciais da época."
    },
    "Cry to Heaven": {
        "isbn": "978-0394523514",
        "publisher": "Alfred A. Knopf",
        "pages": 534,
        "description": "Romance histórico ambientado na Itália do século XVIII, seguindo Tonio Treschi, um jovem nobre castrado contra sua vontade que se torna um famoso cantor castrato."
    },
    "Exit to Eden": {
        "isbn": "978-0877956099",
        "publisher": "Arbor House",
        "pages": 336,
        "description": "Romance erótico sobre um resort BDSM numa ilha privada e a complexa relação entre Lisa, sua criadora, e Elliott, um fotógrafo em busca de fantasias. Publicado sob pseudônimo Anne Rampling."
    },
    "Belinda": {
        "isbn": "978-0877958260",
        "publisher": "Arbor House",
        "pages": 439,
        "description": "Romance sobre Jeremy Walker, um ilustrador de livros infantis, e sua obsessiva relação com Belinda, uma jovem misteriosa de dezesseis anos. Publicado sob pseudônimo Anne Rampling."
    },
    "Servant of the Bones": {
        "isbn": "978-0679433015",
        "publisher": "Alfred A. Knopf",
        "pages": 387,
        "description": "Romance sobrenatural sobre Azriel, um espírito da antiga Babilônia que foi transformado em servo de um osso sagrado, agora buscando vingança e redenção no mundo moderno."
    },
    "Violin": {
        "isbn": "978-0679433026",
        "publisher": "Alfred A. Knopf",
        "pages": 289,
        "description": "Romance gótico sobre Triana, uma viúva assombrada por Stefan, o fantasma de um violinista do século XIX com conexões sobrenaturais e uma história trágica."
    },
}


class Command(BaseCommand):
    help = 'Atualiza livros existentes de um autor com dados editoriais completos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--author',
            type=str,
            default='Anne Rice',
            help='Nome do autor (padrão: Anne Rice)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a atualização sem modificar o banco'
        )
        parser.add_argument(
            '--with-covers',
            action='store_true',
            help='Também baixa capas via Google Books API'
        )

    def handle(self, *args, **options):
        author_name = options['author']
        dry_run = options['dry_run']
        with_covers = options['with_covers']

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.WARNING(f"  ATUALIZADOR DE LIVROS: {author_name}"))
        self.stdout.write("=" * 70)

        if dry_run:
            self.stdout.write(self.style.NOTICE("\n🔍 MODO SIMULAÇÃO\n"))

        # Buscar autor
        author = Author.objects.filter(name__icontains=author_name).first()
        if not author:
            raise CommandError(f"Autor '{author_name}' não encontrado no banco")

        self.stdout.write(f"👤 Autor encontrado: {author.name}")

        # Buscar livros do autor
        books = Book.objects.filter(author=author)
        self.stdout.write(f"📚 Livros no banco: {books.count()}")

        updated = 0
        not_found = 0
        covers_downloaded = 0

        for book in books:
            title = book.title
            self.stdout.write(f"\n📖 {title}")

            # Buscar dados na nossa base
            book_data = ANNE_RICE_BOOKS_DATA.get(title)
            
            if not book_data:
                self.stdout.write(f"   ⚠️  Dados não encontrados no dicionário")
                not_found += 1
                continue

            # Verificar o que precisa atualizar
            updates = []
            
            if not book.isbn and book_data.get('isbn'):
                updates.append(f"ISBN: {book_data['isbn']}")
                if not dry_run:
                    book.isbn = book_data['isbn']
            
            if not book.publisher and book_data.get('publisher'):
                updates.append(f"Editora: {book_data['publisher']}")
                if not dry_run:
                    book.publisher = book_data['publisher']
            
            if not book.page_count and book_data.get('pages'):
                updates.append(f"Páginas: {book_data['pages']}")
                if not dry_run:
                    book.page_count = book_data['pages']
            
            # Atualizar descrição se a atual for muito curta ou genérica
            current_desc = book.description or ''
            new_desc = book_data.get('description', '')
            if len(current_desc) < 100 and len(new_desc) > len(current_desc):
                updates.append("Descrição melhorada")
                if not dry_run:
                    book.description = new_desc

            if updates:
                if not dry_run:
                    book.save()
                self.stdout.write(self.style.SUCCESS(f"   ✅ Atualizado: {', '.join(updates)}"))
                updated += 1
            else:
                self.stdout.write(f"   ⏭️  Já está completo")

            # Baixar capa se solicitado
            if with_covers and not book.cover_image:
                if dry_run:
                    self.stdout.write(f"   📷 [SIMULAÇÃO] Baixaria capa")
                else:
                    self.stdout.write(f"   📷 Baixando capa...")
                    try:
                        result = update_book_cover_from_google(book, force=False)
                        if result:
                            self.stdout.write(self.style.SUCCESS(f"   ✅ Capa baixada!"))
                            covers_downloaded += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"   ⚠️  Capa não encontrada"))
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))

        # Resumo
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("  RESUMO"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"\n✅ Livros atualizados: {updated}")
        self.stdout.write(f"⚠️  Sem dados no dicionário: {not_found}")
        if with_covers:
            self.stdout.write(f"📷 Capas baixadas: {covers_downloaded}")
        
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                "\n⚠️  MODO SIMULAÇÃO - Execute sem --dry-run para aplicar"
            ))

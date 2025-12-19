"""
Setup News Sources Command
Configura fontes RSS padrão para agregação de notícias literárias.
"""

from django.core.management.base import BaseCommand
from news.models import NewsSource


class Command(BaseCommand):
    help = 'Configura fontes RSS padrão de notícias literárias'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todas as fontes existentes antes de adicionar as padrão'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('\n📡 Configurando fontes RSS de notícias literárias...\n'))
        
        if options['clear']:
            deleted, _ = NewsSource.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'🗑️ {deleted} fontes removidas\n'))
        
        # Lista de fontes RSS padrão
        sources = [
            # Google News - Livros e Literatura
            {
                'name': 'Google News - Livros Literatura',
                'url': 'https://news.google.com/rss/search?q=livros+literatura+when:7d&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 10,
                'keywords_include': ['livro', 'autor', 'literatura', 'editora', 'lançamento', 'best-seller', 'livraria'],
                'keywords_exclude': ['política', 'eleição', 'futebol', 'bolsa', 'ações'],
            },
            # Google News - Bestsellers
            {
                'name': 'Google News - Bestsellers',
                'url': 'https://news.google.com/rss/search?q=bestseller+livro+literatura&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 9,
                'keywords_include': ['bestseller', 'mais vendido', 'ranking', 'lista'],
                'keywords_exclude': [],
            },
            # Google News - Prêmios Literários
            {
                'name': 'Google News - Prêmios Literários',
                'url': 'https://news.google.com/rss/search?q=prêmio+literário+OR+nobel+literatura&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 8,
                'keywords_include': ['prêmio', 'nobel', 'jabuti', 'camões', 'goncourt', 'booker', 'pulitzer'],
                'keywords_exclude': [],
            },
            # Google News - Lançamentos de Livros
            {
                'name': 'Google News - Lançamentos',
                'url': 'https://news.google.com/rss/search?q=lançamento+livro+2024+2025&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 9,
                'keywords_include': ['lançamento', 'novo livro', 'estreia', 'publica'],
                'keywords_exclude': [],
            },
            # Google News - Autores Brasileiros
            {
                'name': 'Google News - Autores Brasileiros',
                'url': 'https://news.google.com/rss/search?q=escritor+brasileiro+OR+autor+brasileiro&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 8,
                'keywords_include': ['escritor', 'autor', 'romancista', 'poeta', 'contista'],
                'keywords_exclude': [],
            },
            # Google News - Eventos Literários
            {
                'name': 'Google News - Eventos Literários',
                'url': 'https://news.google.com/rss/search?q=feira+livro+OR+bienal+livro+OR+flip+paraty&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 7,
                'keywords_include': ['feira', 'bienal', 'festival', 'flip', 'evento'],
                'keywords_exclude': [],
            },
            # Google News - Adaptações Cinema/TV
            {
                'name': 'Google News - Adaptações Cinema',
                'url': 'https://news.google.com/rss/search?q=adaptação+livro+filme+OR+série+baseada+livro&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 8,
                'keywords_include': ['adaptação', 'baseado no livro', 'série', 'filme', 'netflix', 'hbo', 'disney'],
                'keywords_exclude': [],
            },
            # Google News - Adaptações Netflix/Streaming
            {
                'name': 'Google News - Netflix Livros',
                'url': 'https://news.google.com/rss/search?q=netflix+baseado+livro+OR+amazon+prime+adaptação&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 7,
                'keywords_include': ['netflix', 'amazon', 'streaming', 'adaptação', 'série'],
                'keywords_exclude': [],
            },
            # Google News - Anime e Manga (PT-BR)
            {
                'name': 'Google News - Anime BR',
                'url': 'https://news.google.com/rss/search?q=anime+novo+estreia+temporada&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 9,
                'keywords_include': ['anime', 'temporada', 'episódio', 'crunchyroll', 'netflix anime'],
                'keywords_exclude': [],
            },
            # Google News - Mangá (PT-BR)
            {
                'name': 'Google News - Mangá BR',
                'url': 'https://news.google.com/rss/search?q=mangá+lançamento+one+piece+OR+dragon+ball+OR+naruto&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 9,
                'keywords_include': ['mangá', 'manga', 'capítulo', 'shonen', 'seinen'],
                'keywords_exclude': [],
            },
            # Google News - Anime Internacional
            {
                'name': 'Google News - Anime EN',
                'url': 'https://news.google.com/rss/search?q=anime+new+season+release&hl=en-US&gl=US&ceid=US:en',
                'source_type': 'rss',
                'priority': 8,
                'keywords_include': ['anime', 'manga', 'crunchyroll', 'funimation'],
                'keywords_exclude': [],
            },
            # Google News - Light Novel
            {
                'name': 'Google News - Light Novel',
                'url': 'https://news.google.com/rss/search?q=light+novel+adaptação+anime&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 7,
                'keywords_include': ['light novel', 'novel', 'isekai', 'adaptação'],
                'keywords_exclude': [],
            },
            # === FONTES ESPECIALIZADAS DE ANIME ===
            # Crunchyroll News
            {
                'name': 'Crunchyroll News',
                'url': 'https://news.google.com/rss/search?q=site:crunchyroll.com+anime&hl=en-US',
                'source_type': 'rss',
                'priority': 10,
                'keywords_include': ['anime', 'crunchyroll', 'season', 'episode', 'streaming'],
                'keywords_exclude': [],
            },
            # Anime News Network
            {
                'name': 'Anime News Network',
                'url': 'https://www.animenewsnetwork.com/newsroom/rss.xml',
                'source_type': 'rss',
                'priority': 10,
                'keywords_include': ['anime', 'manga', 'release', 'adaptation'],
                'keywords_exclude': [],
            },
            # MyAnimeList News
            {
                'name': 'MyAnimeList News',
                'url': 'https://news.google.com/rss/search?q=site:myanimelist.net+anime+news&hl=en-US',
                'source_type': 'rss',
                'priority': 9,
                'keywords_include': ['anime', 'manga', 'myanimelist'],
                'keywords_exclude': [],
            },
            # Otaku News (Brasil)
            {
                'name': 'Otaku News BR',
                'url': 'https://news.google.com/rss/search?q=anime+estreia+2024+2025+brasil&hl=pt-BR&gl=BR',
                'source_type': 'rss',
                'priority': 8,
                'keywords_include': ['anime', 'otaku', 'brasil', 'dublado'],
                'keywords_exclude': [],
            },
            # Google News - Games baseados em livros
            {
                'name': 'Google News - Games Livros',
                'url': 'https://news.google.com/rss/search?q=game+baseado+livro+OR+the+witcher+game&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 6,
                'keywords_include': ['game', 'jogo', 'baseado', 'adaptação', 'witcher'],
                'keywords_exclude': [],
            },
            # Google News - Stephen King (autor popular com muitas adaptações)
            {
                'name': 'Google News - Stephen King',
                'url': 'https://news.google.com/rss/search?q=stephen+king+livro+OR+filme&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 5,
                'keywords_include': [],
                'keywords_exclude': [],
            },
            # Google News - Tolkien
            {
                'name': 'Google News - Tolkien',
                'url': 'https://news.google.com/rss/search?q=tolkien+OR+senhor+anéis+OR+hobbit&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 5,
                'keywords_include': [],
                'keywords_exclude': [],
            },
            # Google News - Harry Potter/J.K. Rowling
            {
                'name': 'Google News - Harry Potter',
                'url': 'https://news.google.com/rss/search?q=harry+potter+OR+jk+rowling&hl=pt-BR&gl=BR&ceid=BR:pt-419',
                'source_type': 'rss',
                'priority': 5,
                'keywords_include': [],
                'keywords_exclude': [],
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for source_data in sources:
            source, created = NewsSource.objects.update_or_create(
                url=source_data['url'],
                defaults={
                    'name': source_data['name'],
                    'source_type': source_data['source_type'],
                    'priority': source_data['priority'],
                    'keywords_include': source_data['keywords_include'],
                    'keywords_exclude': source_data['keywords_exclude'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Criada: {source.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  ○ Atualizada: {source.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} fontes criadas'))
        if updated_count:
            self.stdout.write(self.style.WARNING(f'🔄 {updated_count} fontes atualizadas'))
        
        total = NewsSource.objects.filter(is_active=True).count()
        self.stdout.write(self.style.NOTICE(f'\n📊 Total de fontes ativas: {total}'))
        self.stdout.write(self.style.NOTICE('💡 Dica: Use "python manage.py fetch_news --test" para testar'))

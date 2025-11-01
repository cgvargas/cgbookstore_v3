"""
Sistema de Análise de Preferências do Usuário
Prioriza recomendações baseadas nas prateleiras da biblioteca do usuário.

Hierarquia de Pesos:
1. Favoritos (50%) - Revela gostos fortemente estabelecidos
2. Lidos (30%) - Histórico comprovado de leitura
3. Lendo (15%) - Interesse atual e ativo
4. Quero Ler (5%) - Interesse declarado mas não confirmado
5. Abandonados (0%) - Excluídos das recomendações

Lógica:
- Favoritos têm peso máximo pois representam livros que o usuário ADOROU
- Lidos têm peso alto pois foram efetivamente lidos (confirmação de interesse)
- Lendo têm peso médio (interesse atual, mas ainda não confirmado)
- Quero Ler têm peso baixo (interesse declarado, pode mudar)
- Abandonados são usados apenas para EXCLUSÃO
"""

from django.db.models import Q, Count, Avg
from accounts.models import BookShelf
from core.models import Book
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ShelfWeightConfig:
    """
    Configuração de pesos por tipo de prateleira.

    Soma total = 100% (1.0)
    """
    FAVORITES = 0.50    # 50% - Maior peso
    READ = 0.30         # 30% - Alto peso
    READING = 0.15      # 15% - Médio peso
    TO_READ = 0.05      # 5%  - Baixo peso
    ABANDONED = 0.0     # 0%  - Excluído
    CUSTOM = 0.10       # 10% - Peso médio (prateleiras personalizadas positivas)

    # Mapeamento de shelf_type para peso
    WEIGHTS = {
        'favorites': FAVORITES,
        'read': READ,
        'reading': READING,
        'to_read': TO_READ,
        'abandoned': ABANDONED,
        'custom': CUSTOM,
    }

    @classmethod
    def get_weight(cls, shelf_type):
        """Retorna o peso para um tipo de prateleira."""
        return cls.WEIGHTS.get(shelf_type, 0.0)

    @classmethod
    def get_description(cls, shelf_type):
        """Retorna descrição do peso."""
        descriptions = {
            'favorites': f'Favoritos ({cls.FAVORITES*100:.0f}% - Maior impacto)',
            'read': f'Lidos ({cls.READ*100:.0f}% - Alto impacto)',
            'reading': f'Lendo ({cls.READING*100:.0f}% - Médio impacto)',
            'to_read': f'Quero Ler ({cls.TO_READ*100:.0f}% - Baixo impacto)',
            'abandoned': f'Abandonados ({cls.ABANDONED*100:.0f}% - Excluídos)',
            'custom': f'Personalizadas ({cls.CUSTOM*100:.0f}% - Médio impacto)',
        }
        return descriptions.get(shelf_type, 'Desconhecido')


class UserPreferenceAnalyzer:
    """
    Analisa as preferências do usuário baseado em suas prateleiras.

    Extrai informações de:
    - Gêneros favoritos
    - Autores favoritos
    - Categorias preferidas
    - Padrões de leitura
    """

    def __init__(self, user):
        self.user = user
        self._cache = {}

    def get_weighted_books(self):
        """
        Retorna lista de livros com seus pesos baseados na prateleira.

        Returns:
            list: [{'book': Book, 'weight': float, 'shelf_type': str, 'reason': str}]
        """
        cache_key = 'weighted_books'
        if cache_key in self._cache:
            return self._cache[cache_key]

        shelves = BookShelf.objects.filter(user=self.user).select_related('book')

        weighted_books = []
        stats = defaultdict(int)

        for shelf in shelves:
            weight = ShelfWeightConfig.get_weight(shelf.shelf_type)

            # Abandonados são excluídos
            if weight == 0:
                stats['abandoned'] += 1
                continue

            weighted_books.append({
                'book': shelf.book,
                'weight': weight,
                'shelf_type': shelf.shelf_type,
                'shelf_display': shelf.get_shelf_display(),
                'reason': f'Baseado em {shelf.get_shelf_display()} ({weight*100:.0f}% de influência)'
            })

            stats[shelf.shelf_type] += 1

        # Log estatísticas
        logger.info(
            f"📊 UserPreference [{self.user.username}]: "
            f"Favoritos={stats['favorites']}, "
            f"Lidos={stats['read']}, "
            f"Lendo={stats['reading']}, "
            f"Quero Ler={stats['to_read']}, "
            f"Abandonados={stats['abandoned']}, "
            f"Total Ponderado={len(weighted_books)}"
        )

        # Ordenar por peso (maior primeiro)
        weighted_books.sort(key=lambda x: x['weight'], reverse=True)

        self._cache[cache_key] = weighted_books
        return weighted_books

    def get_top_genres(self, n=5):
        """
        Retorna top N gêneros baseados em pesos das prateleiras.

        Args:
            n: Número de gêneros a retornar

        Returns:
            list: [{'genre': str, 'weight': float, 'count': int}]
        """
        weighted_books = self.get_weighted_books()

        genre_weights = defaultdict(lambda: {'weight': 0.0, 'count': 0})

        for item in weighted_books:
            book = item['book']
            weight = item['weight']

            # Categoria do livro
            if hasattr(book, 'category') and book.category:
                genre = book.category
                genre_weights[genre]['weight'] += weight
                genre_weights[genre]['count'] += 1

        # Converter para lista e ordenar por peso
        top_genres = [
            {'genre': genre, 'weight': data['weight'], 'count': data['count']}
            for genre, data in genre_weights.items()
        ]

        top_genres.sort(key=lambda x: x['weight'], reverse=True)

        genre_list = ', '.join([f"{g['genre']} ({g['weight']:.2f})" for g in top_genres[:3]])
        logger.info(
            f"🎯 Top Genres [{self.user.username}]: {genre_list}"
        )

        return top_genres[:n]

    def get_top_authors(self, n=5):
        """
        Retorna top N autores baseados em pesos das prateleiras.

        Args:
            n: Número de autores a retornar

        Returns:
            list: [{'author': str, 'weight': float, 'count': int}]
        """
        weighted_books = self.get_weighted_books()

        author_weights = defaultdict(lambda: {'weight': 0.0, 'count': 0})

        for item in weighted_books:
            book = item['book']
            weight = item['weight']

            # Autor do livro
            if hasattr(book, 'author') and book.author:
                author = str(book.author)
                author_weights[author]['weight'] += weight
                author_weights[author]['count'] += 1

        # Converter para lista e ordenar por peso
        top_authors = [
            {'author': author, 'weight': data['weight'], 'count': data['count']}
            for author, data in author_weights.items()
        ]

        top_authors.sort(key=lambda x: x['weight'], reverse=True)

        author_list = ', '.join([f"{a['author']} ({a['weight']:.2f})" for a in top_authors[:3]])
        logger.info(
            f"✍️ Top Authors [{self.user.username}]: {author_list}"
        )

        return top_authors[:n]

    def get_preference_profile(self):
        """
        Retorna perfil completo de preferências do usuário.

        Returns:
            dict: {
                'top_genres': list,
                'top_authors': list,
                'total_books': int,
                'shelf_distribution': dict,
                'weighted_books': list
            }
        """
        weighted_books = self.get_weighted_books()

        # Distribuição por prateleira
        shelf_distribution = defaultdict(int)
        for item in weighted_books:
            shelf_distribution[item['shelf_type']] += 1

        profile = {
            'top_genres': self.get_top_genres(n=5),
            'top_authors': self.get_top_authors(n=5),
            'total_books': len(weighted_books),
            'shelf_distribution': dict(shelf_distribution),
            'weighted_books': weighted_books,
        }

        # Log perfil
        top_genre = profile['top_genres'][0]['genre'] if profile['top_genres'] else 'N/A'
        top_author = profile['top_authors'][0]['author'] if profile['top_authors'] else 'N/A'

        logger.info(
            f"👤 Preference Profile [{self.user.username}]: "
            f"Total={profile['total_books']}, "
            f"Top Genre={top_genre}, "
            f"Top Author={top_author}"
        )

        return profile

    def get_similar_books_weighted(self, book, n=10):
        """
        Encontra livros similares priorizando gêneros/autores das prateleiras ponderadas.

        Args:
            book: Livro de referência
            n: Número de livros similares

        Returns:
            list: Livros similares ordenados por relevância
        """
        top_genres = [g['genre'] for g in self.get_top_genres(n=3)]
        top_authors = [a['author'] for a in self.get_top_authors(n=3)]

        # Buscar livros similares
        similar_query = Book.objects.exclude(
            id__in=[item['book'].id for item in self.get_weighted_books()]
        )

        # Priorizar livros do mesmo gênero ou autor favorito
        if hasattr(book, 'category') and book.category in top_genres:
            similar_query = similar_query.filter(category=book.category)

        if hasattr(book, 'author') and str(book.author) in top_authors:
            similar_query = similar_query.filter(author=book.author)

        return list(similar_query[:n])

    def score_book_by_preference(self, book):
        """
        Pontua um livro baseado no perfil de preferências do usuário.

        Critérios:
        - Autor está no top 5? +0.3
        - Gênero está no top 5? +0.3
        - Mesmo autor de favorito? +0.2
        - Mesmo gênero de favorito? +0.2

        Args:
            book: Livro a pontuar

        Returns:
            float: Score de 0.0 a 1.0
        """
        score = 0.0
        reasons = []

        top_genres = [g['genre'] for g in self.get_top_genres(n=5)]
        top_authors = [a['author'] for a in self.get_top_authors(n=5)]

        # Verificar autor
        if hasattr(book, 'author') and book.author:
            author = str(book.author)
            if author in top_authors:
                author_rank = top_authors.index(author) + 1
                author_score = 0.3 * (1.0 - (author_rank - 1) / len(top_authors))
                score += author_score
                reasons.append(f"Autor favorito #{author_rank}")

        # Verificar gênero
        if hasattr(book, 'category') and book.category:
            genre = book.category
            if genre in top_genres:
                genre_rank = top_genres.index(genre) + 1
                genre_score = 0.3 * (1.0 - (genre_rank - 1) / len(top_genres))
                score += genre_score
                reasons.append(f"Gênero favorito #{genre_rank}")

        # Verificar favoritos específicos
        favorites = [
            item['book'] for item in self.get_weighted_books()
            if item['shelf_type'] == 'favorites'
        ]

        for fav in favorites:
            if hasattr(book, 'author') and hasattr(fav, 'author'):
                if book.author == fav.author:
                    score += 0.2
                    reasons.append(f"Mesmo autor de '{fav.title}' (Favorito)")
                    break

        for fav in favorites:
            if hasattr(book, 'category') and hasattr(fav, 'category'):
                if book.category == fav.category:
                    score += 0.2
                    reasons.append(f"Mesmo gênero de '{fav.title}' (Favorito)")
                    break

        # Normalizar (máximo = 1.0)
        score = min(score, 1.0)

        if score > 0:
            logger.debug(
                f"📈 Book Score [{book.title}]: {score:.2f} - {', '.join(reasons)}"
            )

        return score

    def get_statistics(self):
        """
        Retorna estatísticas detalhadas das prateleiras.

        Returns:
            dict: Estatísticas completas
        """
        weighted_books = self.get_weighted_books()

        stats = {
            'total_books': len(weighted_books),
            'total_weight': sum(item['weight'] for item in weighted_books),
            'by_shelf': defaultdict(lambda: {'count': 0, 'weight': 0.0}),
            'weight_distribution': {},
        }

        for item in weighted_books:
            shelf_type = item['shelf_type']
            stats['by_shelf'][shelf_type]['count'] += 1
            stats['by_shelf'][shelf_type]['weight'] += item['weight']

        # Calcular distribuição percentual
        total_weight = stats['total_weight']
        if total_weight > 0:
            for shelf_type, data in stats['by_shelf'].items():
                percentage = (data['weight'] / total_weight) * 100
                stats['weight_distribution'][shelf_type] = f"{percentage:.1f}%"

        return dict(stats)


def print_user_preference_report(user):
    """
    Imprime relatório detalhado de preferências do usuário.
    Útil para debugging e análise.

    Args:
        user: Usuário a analisar
    """
    analyzer = UserPreferenceAnalyzer(user)
    profile = analyzer.get_preference_profile()
    stats = analyzer.get_statistics()

    print("\n" + "="*60)
    print(f"📊 RELATÓRIO DE PREFERÊNCIAS - {user.username}")
    print("="*60)

    print(f"\n📚 Total de Livros: {profile['total_books']}")
    print(f"⚖️  Peso Total: {stats['total_weight']:.2f}")

    print("\n📖 Distribuição por Prateleira:")
    for shelf_type, data in stats['by_shelf'].items():
        weight_pct = stats['weight_distribution'].get(shelf_type, '0%')
        desc = ShelfWeightConfig.get_description(shelf_type)
        print(f"  • {desc}: {data['count']} livros ({weight_pct} do total)")

    print("\n🎯 Top 5 Gêneros Favoritos:")
    for i, genre in enumerate(profile['top_genres'], 1):
        print(f"  {i}. {genre['genre']} - Peso: {genre['weight']:.2f} ({genre['count']} livros)")

    print("\n✍️  Top 5 Autores Favoritos:")
    for i, author in enumerate(profile['top_authors'], 1):
        print(f"  {i}. {author['author']} - Peso: {author['weight']:.2f} ({author['count']} livros)")

    print("\n" + "="*60 + "\n")


# Script de teste
if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
    django.setup()

    from django.contrib.auth.models import User

    # Testar com usuário
    user = User.objects.get(username='claud')
    print_user_preference_report(user)

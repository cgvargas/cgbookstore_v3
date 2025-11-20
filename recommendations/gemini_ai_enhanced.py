"""
Sistema de Recomendações com IA Potencializado.
Integra Gemini AI + Google Books API para recomendações de livros novos.
"""
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
import logging
import json
import requests

logger = logging.getLogger(__name__)


class EnhancedGeminiRecommendationEngine:
    """
    Motor avançado de recomendações usando Gemini AI + Google Books API.

    Funcionalidades:
    1. Exclui livros que o usuário já conhece (lendo, lidos, wishlist)
    2. Busca livros novos no Google Books API
    3. Gera descrições curtas e persuasivas
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = 'gemini-2.5-flash'

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("GEMINI_API_KEY not configured")
            self.model = None

    def is_available(self):
        """Verifica se a API do Gemini está configurada."""
        return self.model is not None

    def generate_enhanced_recommendations(self, user, user_history, n=6):
        """
        Gera recomendações potencializadas com Google Books.

        Args:
            user: Objeto User do Django
            user_history: Lista de dicts com histórico completo do usuário
            n: Número de recomendações desejadas

        Returns:
            Lista de recomendações com dados do Google Books
        """
        if not self.is_available():
            logger.warning("Gemini AI not available")
            return []

        # Extrair livros que o usuário JÁ CONHECE (prateleiras + interações)
        known_books = self._extract_known_books_from_shelves(user)

        # Cache key inclui livros conhecidos
        cache_key = f'gemini_enhanced:{user.id}:{n}:{hash(str(sorted(known_books))[:50])}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.info(f"Using cached enhanced recommendations for {user.username}")
            return cached_result

        try:
            # PASSO 1: Pedir MAIS livros ao Gemini (3x) para compensar filtros
            # Muitos livros serão descartados (sem capa, não encontrados, etc)
            requested_books = n * 3
            prompt = self._build_enhanced_prompt(user, user_history, known_books, requested_books)

            logger.info(f"Calling Gemini AI for {user.username} (requesting {requested_books} books)...")

            # Configurar timeout para evitar requisições travadas
            generation_config = genai.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
            )

            # Adicionar timeout de 40 segundos (multiplataforma - funciona no Windows)
            import threading

            timeout_occurred = [False]  # Lista mutável para compartilhar estado

            def timeout_handler():
                timeout_occurred[0] = True
                logger.warning("Gemini API timeout após 40 segundos")

            # Timer de 40 segundos (multiplataforma)
            timer = threading.Timer(40.0, timeout_handler)
            timer.start()

            try:
                if timeout_occurred[0]:
                    raise TimeoutError("Gemini API timeout antes da chamada")

                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options={'timeout': 40}
                )

                if timeout_occurred[0]:
                    raise TimeoutError("Gemini API timeout após 40 segundos")
            finally:
                # Cancelar timer
                timer.cancel()

            # PASSO 2: Parse das recomendações da IA
            ai_recommendations = self._parse_ai_recommendations(response.text)

            if not ai_recommendations:
                logger.warning("Gemini returned no recommendations")
                return []

            logger.info(f"Gemini suggested {len(ai_recommendations)} books, filtering through Google Books API...")

            # PASSO 3: Enriquecer com dados do Google Books
            enriched_recommendations = []
            books_tried = 0
            books_filtered_no_cover = 0
            books_not_found = 0

            for rec in ai_recommendations:
                books_tried += 1
                google_book = self._search_google_books(rec['title'], rec['author'])

                if google_book:
                    # Usar descrição do Google Books ou razão da IA (mais rápido)
                    description = google_book.get('description', rec['reason'])
                    if description and len(description) > 150:
                        description = description[:147] + '...'

                    enriched_recommendations.append({
                        'title': google_book.get('title', rec['title']),
                        'author': google_book.get('author', rec['author']),
                        'cover_image': google_book.get('cover_url'),
                        'google_books_id': google_book.get('id'),
                        'description': description or rec['reason'],
                        'reason': rec['reason'],
                        'score': 0.95,
                        'source': 'google_books'
                    })

                    logger.debug(f"✓ Book added: {rec['title']} (has cover)")

                    if len(enriched_recommendations) >= n:
                        logger.info(f"✓ Reached target of {n} books, stopping search")
                        break
                elif google_book is None:
                    # None significa que foi filtrado (sem capa ou não encontrado)
                    logger.debug(f"✗ Book filtered: {rec['title']} (no cover or not found)")
                    books_filtered_no_cover += 1
                else:
                    books_not_found += 1

            # Log de estatísticas
            logger.info(
                f"📊 Stats: {books_tried} tried, {len(enriched_recommendations)} added, "
                f"{books_filtered_no_cover} filtered (no cover/not found)"
            )

            # Cachear por 24 horas (86400 segundos)
            cache.set(
                cache_key,
                enriched_recommendations,
                timeout=86400  # 24 horas
            )

            logger.info(f"Generated {len(enriched_recommendations)} enhanced recommendations for {user.username}")

            return enriched_recommendations

        except TimeoutError as e:
            logger.error(f"Timeout calling Gemini AI: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in enhanced recommendations: {e}", exc_info=True)
            return []

    def _extract_known_books_from_shelves(self, user):
        """
        Extrai RIGOROSAMENTE todos os livros que o usuário já conhece.

        Verifica:
        1. PRATELEIRAS (BookShelf): favorites, to_read, reading, read, abandoned, custom
        2. INTERAÇÕES (UserBookInteraction): todos os tipos

        Returns:
            Lista de títulos de livros em lowercase
        """
        from accounts.models import BookShelf
        from .models import UserBookInteraction

        known_books = set()

        # 1. PRATELEIRAS (prioritário e mais confiável)
        shelves = BookShelf.objects.filter(user=user).select_related('book')
        for shelf in shelves:
            if shelf.book and shelf.book.title:
                known_books.add(shelf.book.title.lower().strip())

        # 2. INTERAÇÕES
        interactions = UserBookInteraction.objects.filter(user=user).select_related('book')
        for interaction in interactions:
            if interaction.book and interaction.book.title:
                known_books.add(interaction.book.title.lower().strip())

        logger.info(f"User {user.username} knows {len(known_books)} books (shelves + interactions)")

        return list(known_books)

    def _build_enhanced_prompt(self, user, user_history, known_books, n):
        """
        Constrói prompt otimizado pedindo livros NOVOS.
        """
        # Extrair informações do perfil
        read_books = [item['title'] for item in user_history if item.get('interaction_type') in ['read', 'completed']]
        reading_books = [item['title'] for item in user_history if item.get('interaction_type') in ['reading', 'current']]
        wishlist_books = [item['title'] for item in user_history if item.get('interaction_type') == 'wishlist']

        # Extrair gêneros favoritos
        favorite_genres = self._extract_genres(user_history)

        # Montar lista de livros conhecidos
        known_books_str = ', '.join(known_books[:20]) if known_books else 'Nenhum'

        prompt = f"""Recomende {n} livros novos para {user.username}.

JÁ CONHECE (NÃO recomendar): {known_books_str}

PERFIL:
- Leu: {', '.join(read_books[:3]) if read_books else 'nenhum'}
- Lendo: {', '.join(reading_books[:2]) if reading_books else 'nenhum'}
- Gêneros: {', '.join(favorite_genres[:3]) if favorite_genres else 'variados'}

REGRAS:
1. NUNCA recomende livros da lista "JÁ CONHECE"
2. Títulos EXATOS (Google Books)
3. Razão: 1 linha curta

JSON:
{{
  "recommendations": [
    {{"title": "Título Completo", "author": "Autor", "reason": "Razão curta"}}
  ]
}}

Responda SÓ o JSON."""

        return prompt

    def _extract_genres(self, user_history):
        """Extrai gêneros favoritos do histórico."""
        genres = []
        for item in user_history:
            if 'categories' in item and item['categories']:
                book_genres = [g.strip() for g in str(item['categories']).split(',')]
                genres.extend(book_genres)

        # Contar frequência
        genre_counts = {}
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Top 5 gêneros
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, _ in sorted_genres[:5]]

    def _parse_ai_recommendations(self, response_text):
        """Parse da resposta JSON do Gemini."""
        try:
            # Limpar markdown
            clean_text = response_text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text.replace('```json', '').replace('```', '').strip()
            elif clean_text.startswith('```'):
                clean_text = clean_text.replace('```', '').strip()

            # Parse JSON
            data = json.loads(clean_text)

            recommendations = []
            for rec in data.get('recommendations', []):
                recommendations.append({
                    'title': rec.get('title', '').strip(),
                    'author': rec.get('author', '').strip(),
                    'reason': rec.get('reason', '').strip()
                })

            return recommendations

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Response: {response_text}")
            return []
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return []

    def _search_google_books(self, title, author):
        """
        Busca livro no Google Books API com múltiplas estratégias de fallback.

        Returns:
            Dict com dados do livro ou None
        """
        try:
            url = 'https://www.googleapis.com/books/v1/volumes'

            # ESTRATÉGIA 1: Busca completa (título + autor) em português
            query = f'intitle:{title} inauthor:{author}'
            params = {
                'q': query,
                'maxResults': 3,  # Pegar 3 resultados para ter mais opções
                'langRestrict': 'pt',
                'printType': 'books'
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Se não encontrou, tentar sem restrição de idioma
            if data.get('totalItems', 0) == 0:
                logger.debug(f"No results in PT for '{title}', trying all languages...")
                params['langRestrict'] = ''
                response = requests.get(url, params=params, timeout=5)
                data = response.json()

            # ESTRATÉGIA 2: Se ainda não encontrou, buscar só pelo título
            if data.get('totalItems', 0) == 0:
                logger.debug(f"No results with author, trying title only: '{title}'")
                params['q'] = f'intitle:{title}'
                params['maxResults'] = 5  # Mais resultados para compensar
                response = requests.get(url, params=params, timeout=5)
                data = response.json()

            # ESTRATÉGIA 3: Última tentativa - busca genérica
            if data.get('totalItems', 0) == 0:
                logger.debug(f"No results with intitle, trying general search")
                params['q'] = f'{title} {author}'
                response = requests.get(url, params=params, timeout=5)
                data = response.json()

            if data.get('totalItems', 0) == 0:
                logger.warning(f"Book not found on Google Books after all strategies: {title} by {author}")
                return None

            # Iterar pelos resultados e pegar o primeiro COM CAPA
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})

                # Extrair imagem da capa (maior qualidade disponível)
                image_links = volume_info.get('imageLinks', {})
                cover_url = (
                    image_links.get('large') or
                    image_links.get('medium') or
                    image_links.get('thumbnail') or
                    image_links.get('smallThumbnail')
                )

                # Se este resultado tem capa, usar ele!
                if cover_url:
                    # Converter para HTTPS
                    if cover_url.startswith('http:'):
                        cover_url = cover_url.replace('http:', 'https:')

                    logger.debug(f"✓ Found book with cover: {volume_info.get('title')}")

                    return {
                        'id': item.get('id'),
                        'title': volume_info.get('title'),
                        'author': ', '.join(volume_info.get('authors', [author])),
                        'description': volume_info.get('description', ''),
                        'cover_url': cover_url,
                        'google_books_link': volume_info.get('infoLink'),
                        'preview_link': volume_info.get('previewLink'),
                        'publisher': volume_info.get('publisher'),
                        'published_date': volume_info.get('publishedDate'),
                        'page_count': volume_info.get('pageCount'),
                        'categories': volume_info.get('categories', []),
                        'average_rating': volume_info.get('averageRating'),
                        'ratings_count': volume_info.get('ratingsCount')
                    }

            # Se chegou aqui, encontrou resultados mas nenhum tinha capa
            logger.warning(f"Book '{title}' found but has no cover in any result, filtering out")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Books API error for '{title}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error searching Google Books for '{title}': {e}")
            return None

    def _generate_short_description(self, title, author, full_description, ai_reason):
        """
        Gera descrição curta e atrativa usando IA.

        Args:
            title: Título do livro
            author: Autor
            full_description: Descrição completa do Google Books
            ai_reason: Razão da recomendação gerada pela IA

        Returns:
            String com descrição curta (2-3 linhas)
        """
        try:
            # Truncar descrição longa
            desc_snippet = full_description[:300] if full_description else ''

            prompt = f"""
Crie uma descrição CURTA e ATRATIVA para o livro "{title}" de {author}.

DESCRIÇÃO ORIGINAL (resumo):
{desc_snippet}

POR QUE FOI RECOMENDADO:
{ai_reason}

INSTRUÇÕES:
1. Máximo de 2-3 linhas (cerca de 100 caracteres)
2. Seja persuasivo e desperte curiosidade
3. Foque no que torna o livro especial
4. Use tom conversacional e amigável
5. NÃO use aspas ou formatação especial

Responda APENAS com o texto da descrição, sem markdown ou formatação.
"""

            response = self.model.generate_content(prompt)
            short_desc = response.text.strip()

            # Limpar possíveis aspas
            short_desc = short_desc.replace('"', '').replace("'", '').strip()

            # Limitar tamanho
            if len(short_desc) > 200:
                short_desc = short_desc[:197] + '...'

            return short_desc

        except Exception as e:
            logger.error(f"Error generating short description: {e}")
            # Fallback: usar razão da IA ou snippet da descrição
            return ai_reason if len(ai_reason) < 150 else desc_snippet[:147] + '...'

"""
Integração com Google Gemini AI para recomendações premium.
"""
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
import logging
import json
import time

logger = logging.getLogger(__name__)


class GeminiRecommendationEngine:
    """
    Motor de recomendações usando Google Gemini AI com lazy loading do modelo.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = 'gemini-1.5-flash'  # Atualizado para o modelo mais recente e eficiente
        self.request_timeout = 45  # Aumentado para dar mais margem
        self._model = None  # Atributo privado para o modelo, começa como None

    @property
    def model(self):
        """
        Propriedade que inicializa o modelo do Gemini na primeira vez que é acessado.
        Isso evita a inicialização lenta durante o boot do servidor.
        """
        # Se o modelo já foi inicializado, apenas o retorne
        if self._model:
            return self._model

        # Se não há API key, não faz nada
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. AI recommendations will be disabled.")
            return None
        
        # Bloco de inicialização (só roda uma vez)
        logger.info(f"Inicializando o modelo Gemini ({self.model_name}) pela primeira vez...")
        try:
            genai.configure(api_key=self.api_key)
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
            # A inicialização lenta acontece aqui!
            self._model = genai.GenerativeModel(
                self.model_name,
                generation_config=generation_config
            )
            logger.info("Modelo Gemini inicializado com sucesso.")
            return self._model
        except Exception as e:
            logger.error(f"Falha ao inicializar o modelo Gemini: {e}", exc_info=True)
            # Define como None para não tentar de novo
            self._model = None 
            return None

    def is_available(self):
        """Verifica se a API do Gemini está configurada e o modelo pode ser carregado."""
        return self.api_key is not None

    def generate_recommendations(self, user, user_history, n=5):
        """
        Gera recomendações personalizadas usando Gemini AI.
        """
        # Acessar self.model aqui irá acionar a inicialização na primeira vez
        if not self.is_available() or not self.model:
            logger.warning("Gemini AI not available")
            return []

        cache_key = f'gemini_rec:{user.id}:{n}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.info(f"[CACHE HIT] Returning cached recommendations for user {user.username}")
            return cached_result
        
        # O resto do seu código continua igual...
        logger.info(f"[CACHE MISS] Generating new AI recommendations for user {user.username}")
        start_time = time.time()

        try:
            prompt = self._build_prompt(user, user_history, n)
            logger.info(f"Calling Gemini API with timeout of {self.request_timeout}s...")

            response = self.model.generate_content(
                prompt,
                request_options={'timeout': self.request_timeout}
            )
            api_time = time.time() - start_time
            logger.info(f"Gemini API responded in {api_time:.2f}s")
            
            recommendations = self._parse_recommendations(response.text)

            if recommendations:
                cache.set(cache_key, recommendations, timeout=3600) # Cache por 1 hora
                logger.info(f"Generated {len(recommendations)} AI recommendations for {user.username}")

            return recommendations

        except Exception as e:
            logger.error(f"Error in generate_recommendations for user {user.username}: {e}", exc_info=True)
            return []
    
    # ... cole o resto dos seus métodos (_build_prompt, _parse_recommendations, etc.) aqui ...
    # ... eles não precisam de nenhuma alteração ...
    def _build_prompt(self, user, user_history, n):
        """
        Constrói o prompt para o Gemini baseado no histórico do usuário.
        """
        # Extrair informações do histórico
        read_books = [item['title'] for item in user_history if item['interaction_type'] in ['read', 'completed']]
        favorite_genres = self._extract_genres(user_history)

        prompt = f"""
                    Você é um especialista em recomendação de livros. Baseado no perfil do usuário abaixo,
                    recomende {n} livros que ele provavelmente vai adorar.

                    PERFIL DO USUÁRIO:
                    - Nome: {user.username}
                    - Livros já lidos: {', '.join(read_books[:10]) if read_books else 'Nenhum ainda'}
                    - Gêneros favoritos: {', '.join(favorite_genres) if favorite_genres else 'Variados'}
                    - Total de livros lidos: {len(read_books)}

                    INSTRUÇÕES:
                    1. Recomende {n} livros DIFERENTES dos que o usuário já leu
                    2. Para cada livro, forneça:
                    - Título completo
                    - Autor
                    - Uma justificativa personalizada (por que esse livro é perfeito para o usuário)
                    3. Considere os gostos e histórico do usuário
                    4. Seja específico e persuasivo nas justificativas

                    FORMATO DE RESPOSTA (JSON):
                    {{
                    "recommendations": [
                        {{
                        "title": "Título do Livro",
                        "author": "Autor",
                        "reason": "Justificativa detalhada e personalizada"
                        }}
                    ]
                    }}

                    Responda APENAS com o JSON, sem texto adicional.
                    """
        return prompt

    def _extract_genres(self, user_history):
        """
        Extrai gêneros mais frequentes do histórico do usuário.
        """
        genres = []
        for item in user_history:
            if 'categories' in item and item['categories']:
                # Assume que categories é uma string separada por vírgulas
                book_genres = [g.strip() for g in item['categories'].split(',')]
                genres.extend(book_genres)

        # Contar frequência
        genre_counts = {}
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Retornar top 5 gêneros
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, _ in sorted_genres[:5]]

    def _parse_recommendations(self, response_text):
        """
        Faz parsing da resposta JSON do Gemini.
        """
        try:
            # Limpar possíveis marcações markdown
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
                    'title': rec.get('title', ''),
                    'author': rec.get('author', ''),
                    'reason': rec.get('reason', ''),
                    'score': 0.95,  # Score alto para recomendações de IA
                })

            return recommendations

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return []

        except Exception as e:
            logger.error(f"Error parsing Gemini recommendations: {e}")
            return []

    def explain_recommendation(self, user, book):
        """
        Gera uma explicação personalizada de por que um livro é recomendado para o usuário.

        Args:
            user: Objeto User
            book: Objeto Book

        Returns:
            String com a explicação
        """
        if not self.is_available():
            return "Recomendado baseado em suas preferências."

        cache_key = f'gemini_explain:{user.id}:{book.id}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.debug(f"[CACHE HIT] Explanation for book {book.id}")
            return cached_result

        logger.debug(f"[CACHE MISS] Generating explanation for book {book.id}")

        try:
            prompt = f"""
                        Explique em 2-3 frases por que o livro "{book.title}" de {book.author}
                        seria uma ótima leitura para o usuário {user.username}, considerando:

                        - Descrição do livro: {book.description[:500] if book.description else 'Não disponível'}
                        - Categorias: {book.categories if hasattr(book, 'categories') else 'Ficção'}

                        Seja persuasivo e específico. Use tom amigável e conversacional.
                        """

            response = self.model.generate_content(
                prompt,
                request_options={'timeout': self.request_timeout}
            )
            explanation = response.text.strip()

            # Cachear por 24 horas
            cache.set(
                cache_key,
                explanation,
                timeout=settings.RECOMMENDATIONS_CONFIG['SIMILARITY_CACHE_TIMEOUT']
            )

            logger.debug(f"Generated explanation for book {book.id}")
            return explanation

        except TimeoutError as e:
            logger.error(f"Timeout generating explanation for book {book.id}: {e}")
            return "Recomendado baseado em suas preferências."
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Recomendado baseado em suas preferências."

    def generate_reading_insights(self, user, user_history):
        """
        Gera insights sobre os hábitos de leitura do usuário.

        Args:
            user: Objeto User
            user_history: Lista de interações do usuário

        Returns:
            Dict com insights
        """
        if not self.is_available():
            return {}

        cache_key = f'gemini_insights:{user.id}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.info(f"[CACHE HIT] Returning cached insights for user {user.username}")
            return cached_result

        logger.info(f"[CACHE MISS] Generating reading insights for user {user.username}")

        try:
            read_books = [
                item['title']
                for item in user_history
                if item['interaction_type'] in ['read', 'completed']
            ]

            if not read_books:
                logger.debug(f"No read books found for user {user.username}")
                return {}

            prompt = f"""
                        Analise o perfil de leitura do usuário {user.username} e forneça insights:

                        LIVROS LIDOS ({len(read_books)}):
                        {', '.join(read_books[:20])}

                        Forneça:
                        1. Principais temas/gêneros de interesse
                        2. Padrões de leitura identificados
                        3. Sugestões de próximos passos de leitura

                        FORMATO DE RESPOSTA (JSON):
                        {{
                        "main_themes": ["tema1", "tema2"],
                        "reading_patterns": "Descrição dos padrões",
                        "suggestions": "Sugestões personalizadas"
                        }}

                        Responda APENAS com o JSON.
                        """

            response = self.model.generate_content(
                prompt,
                request_options={'timeout': self.request_timeout}
            )
            clean_text = response.text.strip()

            if clean_text.startswith('```json'):
                clean_text = clean_text.replace('```json', '').replace('```', '').strip()
            elif clean_text.startswith('```'):
                clean_text = clean_text.replace('```', '').strip()

            insights = json.loads(clean_text)

            # Cachear por 24 horas
            cache.set(
                cache_key,
                insights,
                timeout=settings.RECOMMENDATIONS_CONFIG['SIMILARITY_CACHE_TIMEOUT']
            )

            logger.info(f"Generated reading insights for user {user.username}")
            return insights

        except TimeoutError as e:
            logger.error(f"Timeout generating insights for user {user.username}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error generating insights: {e}", exc_info=True)
            return {}

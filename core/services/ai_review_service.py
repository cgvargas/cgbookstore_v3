import json
import logging
from django.conf import settings
from django.core.cache import cache
from core.services.ai_provider_service import AIProviderFactory

logger = logging.getLogger(__name__)


class AIReviewService:
    """
    Serviço de Inteligência Artificial para gerar resenhas e análises de livros.
    Utiliza a camada de abstração de provedores da CG.BookStore.
    """

    RATE_LIMIT_CACHE_PREFIX = 'ai_provider_rate_limited'
    PROVIDER_KEY_SETTINGS = {
        'gemini': 'GEMINI_API_KEY',
        'groq': 'GROQ_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'claude': 'CLAUDE_API_KEY',
    }

    @classmethod
    def _provider_names(cls):
        primary = str(getattr(settings, 'AI_PROVIDER', 'mock') or 'mock').lower()
        configured_fallbacks = getattr(settings, 'AI_FALLBACK_PROVIDERS', ('gemini',))
        if isinstance(configured_fallbacks, str):
            configured_fallbacks = configured_fallbacks.split(',')

        names = [primary]
        for name in configured_fallbacks:
            normalized_name = str(name or '').strip().lower()
            if normalized_name and normalized_name not in names:
                names.append(normalized_name)
        return names

    @classmethod
    def _is_provider_configured(cls, provider_name):
        setting_name = cls.PROVIDER_KEY_SETTINGS.get(provider_name)
        if not setting_name:
            return provider_name in {'local', 'mock'}
        return bool(getattr(settings, setting_name, ''))

    @staticmethod
    def _is_rate_limit_error(error):
        status_code = getattr(error, 'status_code', None)
        response = getattr(error, 'response', None)
        response_status = getattr(response, 'status_code', None)
        error_text = str(error).lower()
        return (
            status_code == 429
            or response_status == 429
            or '429' in error_text
            or 'rate limit' in error_text
            or 'rate_limit_exceeded' in error_text
            or 'quota' in error_text
            or 'tokens per day' in error_text
        )

    @classmethod
    def _generate_json_with_fallback(cls, prompt, feature_name):
        provider_names = cls._provider_names()
        primary_name = provider_names[0]
        cooldown = max(1, int(getattr(settings, 'AI_RATE_LIMIT_COOLDOWN_SECONDS', 1200)))
        attempted_provider = False
        configured_provider_seen = False

        for provider_name in provider_names:
            if not cls._is_provider_configured(provider_name):
                continue
            configured_provider_seen = True

            cache_key = f'{cls.RATE_LIMIT_CACHE_PREFIX}:{provider_name}'
            if cache.get(cache_key):
                logger.info(
                    "Provedor de IA %s temporariamente suspenso por rate limit.",
                    provider_name,
                )
                continue

            attempted_provider = True
            try:
                provider = AIProviderFactory.get_provider(provider_name)
                return provider.generate_json(prompt=prompt, feature_name=feature_name)
            except Exception as error:
                if cls._is_rate_limit_error(error):
                    cache.set(cache_key, True, cooldown)
                    logger.warning(
                        "Rate limit do provedor %s; tentando fallback disponível.",
                        provider_name,
                    )
                    continue

                if provider_name != primary_name:
                    logger.warning(
                        "Fallback de IA %s indisponível: %s",
                        provider_name,
                        error.__class__.__name__,
                    )
                    continue
                raise

        if attempted_provider or configured_provider_seen:
            logger.warning("Nenhum provedor de IA disponível após rate limit/fallback.")
        else:
            logger.warning("Nenhum provedor de IA configurado e disponível.")
        return None

    @staticmethod
    def generate_review(book) -> dict:
        """
        Gera uma análise completa da obra utilizando o provedor de IA ativo.
        Retorna um dicionário estruturado com as informações da obra.
        """
        try:
            author_name = book.author.name if book.author else 'Desconhecido'
            category_name = book.category.name if book.category else 'Literatura'
            description = book.description or 'Sem descrição disponível.'
            page_count = book.page_count or 'cerca de 300'
            
            prompt = f"""
            Você é o assistente literário oficial de Inteligência Artificial da rede social CG.BookStore.
            Sua missão é realizar uma análise literária e de experiência de leitura de alta qualidade para o seguinte livro:
            Título: "{book.title}"
            Subtítulo: "{book.subtitle or ''}"
            Autor: "{author_name}"
            Categoria/Gênero: "{category_name}"
            Sinopse/Descrição: "{description[:800]}"
            
            Gere uma análise estruturada contendo exatamente as informações solicitadas em formato JSON válido.
            IMPORTANTE: Responda APENAS com o JSON. Não inclua introduções, marcações markdown como ```json ou qualquer texto extra.
            
            Estrutura do JSON esperado (todas as chaves em português):
            {{
                "resumo": "Uma análise resumida e atrativa da obra (exatamente de 3 a 4 sentenças), explicando o seu valor central e impacto literário.",
                "perfil_leitor": "Uma breve descrição em 1 sentença do perfil do leitor ideal para este livro.",
                "faixa_etaria": "Faixa etária sugerida (ex: 'Livre', '12+', '14+', '16+', '18+').",
                "complexidade": "Nível de complexidade da leitura (ex: 'Fácil', 'Média', 'Alta').",
                "tempo_leitura": "Tempo médio estimado para conclusão da leitura em formato legível (ex: '8 horas', '12 horas'). Baseie-se no fato do livro conter {page_count} páginas.",
                "temas_principais": ["Tema 1", "Tema 2", "Tema 3"],
                "nota_geral": 9.2
            }}
            """
            
            # Chama o gerador JSON da fábrica de provedores
            data = AIReviewService._generate_json_with_fallback(
                prompt=prompt,
                feature_name="book_review"
            )
            
            # Valida tipos de dados básicos para evitar problemas no frontend
            if data:
                data['nota_geral'] = float(data.get('nota_geral', 0.0))
                if not isinstance(data.get('temas_principais'), list):
                    data['temas_principais'] = []
                
            return data
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise de IA para o livro {book.title} (ID: {book.id}): {str(e)}")
            return None

    @staticmethod
    def generate_expanded_analysis(book) -> dict:
        """
        Gera uma análise literária expandida (Curiosidades, Contexto Histórico, 
        Perfil de Personagens e Relações de Universo) usando o provedor de IA ativo.
        Retorna um dicionário estruturado.
        """
        try:
            author_name = book.author.name if book.author else 'Desconhecido'
            category_name = book.category.name if book.category else 'Literatura'
            description = book.description or 'Sem descrição disponível.'
            
            prompt = f"""
            Você é um crítico literário sênior e analista oficial da rede social CG.BookStore.
            Sua missão é gerar uma análise literária expandida e rica para o seguinte livro:
            Título: "{book.title}"
            Autor: "{author_name}"
            Categoria: "{category_name}"
            Descrição: "{description[:800]}"
            
            Gere um JSON estruturado contendo exatamente as seguintes chaves e informações em português:
            {{
                "contexto_historico": "Explique em 2 ou 3 sentenças o contexto histórico ou biográfico de escrita da obra, o que inspirou o autor e o impacto sociocultural da época.",
                "curiosidades": [
                    "Curiosidade 1 sobre o livro, autor, processo de escrita ou recepção.",
                    "Curiosidade 2...",
                    "Curiosidade 3..."
                ],
                "personagens_principais": [
                    {{
                        "nome": "Nome do Personagem 1",
                        "papel": "Breve descrição do papel e importância dele na trama (máximo 1 sentença)."
                    }},
                    {{
                        "nome": "Nome do Personagem 2",
                        "papel": "Breve descrição..."
                    }}
                ],
                "conexoes_universo": "Diga se o livro faz parte de um universo maior, série ou saga literária. Sugira qual a relação temática dele com outras obras do mesmo autor ou gênero em 2 sentenças."
            }}
            
            IMPORTANTE: Responda APENAS com o JSON válido. Não inclua blocos markdown (como ```json) ou qualquer outro texto explicativo.
            """
            
            data = AIReviewService._generate_json_with_fallback(
                prompt=prompt,
                feature_name="book_review"
            )
            
            return data
        except Exception as e:
            logger.error(f"Erro ao gerar análise expandida de IA para o livro {book.title} (ID: {book.id}): {str(e)}")
            return None

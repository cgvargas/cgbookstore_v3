import json
import logging
from django.conf import settings
from core.services.ai_provider_service import AIProviderFactory

logger = logging.getLogger(__name__)


class AIReviewService:
    """
    Serviço de Inteligência Artificial para gerar resenhas e análises de livros.
    Utiliza a camada de abstração de provedores da CG.BookStore.
    """

    @staticmethod
    def generate_review(book) -> dict:
        """
        Gera uma análise completa da obra utilizando o provedor de IA ativo.
        Retorna um dicionário estruturado com as informações da obra.
        """
        try:
            provider = AIProviderFactory.get_provider()
            
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
            data = provider.generate_json(
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
            provider = AIProviderFactory.get_provider()
            
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
            
            data = provider.generate_json(
                prompt=prompt,
                feature_name="book_review"
            )
            
            return data
        except Exception as e:
            logger.error(f"Erro ao gerar análise expandida de IA para o livro {book.title} (ID: {book.id}): {str(e)}")
            return None


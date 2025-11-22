"""
Serviço de integração com Google Gemini AI para o chatbot literário.
"""
from django.conf import settings
from django.core.cache import cache
from core.models import Book, Category
import logging

logger = logging.getLogger(__name__)

# Lazy loading para Google Gemini AI
_genai_loaded = False
genai = None


def _load_genai():
    """Carrega google.generativeai apenas quando necessário (lazy loading)."""
    global _genai_loaded, genai
    if not _genai_loaded:
        try:
            import google.generativeai as _genai
            genai = _genai
            _genai_loaded = True
            logger.info("google.generativeai loaded successfully for chatbot")
        except ImportError as e:
            logger.error(f"Failed to import google.generativeai: {e}")
            genai = None
            _genai_loaded = True
    return genai


class GeminiChatService:
    """
    Serviço de chatbot literário usando Google Gemini AI.
    Especializado em recomendações e discussões sobre livros.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        # Usar gemini-pro que é o modelo estável e disponível
        # Alternativas: 'gemini-1.5-pro', 'gemini-1.5-flash-latest'
        self.model_name = 'gemini-1.5-pro'
        self.request_timeout = 30
        self._model = None
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        """
        Constrói o prompt do sistema que define o comportamento do chatbot.
        Inclui informações sobre o catálogo de livros disponíveis.
        """
        # Buscar algumas categorias para contexto
        categories = Category.objects.all()[:10]
        categories_text = ', '.join([cat.name for cat in categories]) if categories.exists() else 'Ficção, Romance, Fantasia, Mistério'

        # Contar livros no catálogo
        book_count = Book.objects.count()

        system_prompt = f"""Você é um assistente literário especializado da CG.BookStore, uma livraria virtual brasileira.

SUAS CARACTERÍSTICAS:
- Você é apaixonado por literatura e conhece profundamente diversos gêneros
- Você é amigável, prestativo e entusiasta
- Você fala português brasileiro de forma natural e acessível
- Você adapta suas recomendações ao perfil e preferências do usuário

NOSSO CATÁLOGO:
- Temos {book_count} livros disponíveis
- Categorias principais: {categories_text}
- Trabalhamos com diversos gêneros literários

SUAS FUNÇÕES:
1. Recomendar livros baseado nas preferências do usuário
2. Discutir sobre literatura, autores e gêneros
3. Ajudar a encontrar o livro perfeito para cada momento
4. Responder perguntas sobre enredos, temas e estilos literários
5. Sugerir leituras para diferentes perfis (iniciantes, avançados, etc.)

DIRETRIZES:
- Seja sempre positivo e encorajador sobre leitura
- Faça perguntas para entender melhor as preferências
- Dê recomendações específicas quando possível
- Seja conciso mas informativo (respostas de 3-5 parágrafos no máximo)
- Se não souber algo específico do nosso catálogo, seja honesto mas ofereça alternativas
- Use emojis ocasionalmente para tornar a conversa mais amigável 📚
- Nunca invente informações sobre livros que não conhece

EXEMPLOS DE PERGUNTAS QUE VOCÊ PODE FAZER:
- "Que tipo de histórias você mais gosta?"
- "Prefere algo mais leve ou profundo?"
- "Já leu algum livro que te marcou?"
- "Está procurando por qual gênero especificamente?"

Lembre-se: Seu objetivo é criar uma conexão com o leitor e ajudá-lo a descobrir sua próxima grande leitura! 📖"""

        return system_prompt

    @property
    def model(self):
        """
        Propriedade que inicializa o modelo do Gemini na primeira vez que é acessado.
        """
        if self._model:
            return self._model

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. Chatbot will be disabled.")
            return None

        _genai = _load_genai()
        if _genai is None:
            logger.error("Failed to load google.generativeai module")
            return None

        logger.info(f"Inicializando modelo Gemini para chatbot ({self.model_name})...")
        try:
            _genai.configure(api_key=self.api_key)
            generation_config = {
                'temperature': 0.9,  # Mais criativo para conversação
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 1024,  # Respostas mais concisas
            }

            self._model = _genai.GenerativeModel(
                self.model_name,
                generation_config=generation_config,
                system_instruction=self._system_prompt
            )
            logger.info("Modelo Gemini para chatbot inicializado com sucesso")
            return self._model
        except Exception as e:
            logger.error(f"Falha ao inicializar modelo Gemini para chatbot: {e}", exc_info=True)
            self._model = None
            return None

    def is_available(self):
        """Verifica se o serviço está disponível."""
        return self.api_key is not None and self.model is not None

    def get_response(self, user_message, conversation_history=None):
        """
        Gera uma resposta do chatbot para a mensagem do usuário.

        Args:
            user_message (str): Mensagem do usuário
            conversation_history (list): Lista de dicts com histórico [{'role': 'user'/'assistant', 'message': '...'}]

        Returns:
            dict: {'success': bool, 'response': str, 'error': str}
        """
        if not self.is_available():
            return {
                'success': False,
                'response': None,
                'error': 'Serviço de chatbot não disponível. Verifique a configuração da API Key.'
            }

        try:
            # Iniciar uma sessão de chat
            chat = self.model.start_chat(history=[])

            # Se houver histórico, adicionar ao contexto
            if conversation_history:
                # Converter histórico para formato do Gemini
                for msg in conversation_history[-10:]:  # Últimas 10 mensagens
                    role = 'user' if msg['role'] == 'user' else 'model'
                    chat.history.append({
                        'role': role,
                        'parts': [msg['message']]
                    })

            # Enviar mensagem e obter resposta
            logger.info(f"Enviando mensagem ao Gemini: {user_message[:100]}...")
            response = chat.send_message(user_message)

            bot_response = response.text.strip()
            logger.info(f"Resposta recebida do Gemini: {bot_response[:100]}...")

            return {
                'success': True,
                'response': bot_response,
                'error': None
            }

        except Exception as e:
            logger.error(f"Erro ao gerar resposta do chatbot: {e}", exc_info=True)
            return {
                'success': False,
                'response': None,
                'error': f'Erro ao processar mensagem: {str(e)}'
            }

    def get_book_recommendations(self, user_preferences, n=5):
        """
        Gera recomendações específicas de livros baseado nas preferências.

        Args:
            user_preferences (str): Descrição das preferências do usuário
            n (int): Número de recomendações

        Returns:
            dict: {'success': bool, 'recommendations': str, 'error': str}
        """
        if not self.is_available():
            return {
                'success': False,
                'recommendations': None,
                'error': 'Serviço não disponível'
            }

        try:
            # Buscar livros do catálogo para contexto
            books = Book.objects.select_related('category').all()[:50]
            book_list = []
            for book in books:
                book_list.append(f"- {book.title} ({book.category.name if book.category else 'Geral'})")

            catalog_context = "\n".join(book_list[:20])  # Primeiros 20 livros

            prompt = f"""Com base nas seguintes preferências do usuário:
"{user_preferences}"

E considerando alguns livros do nosso catálogo:
{catalog_context}

Por favor, recomende {n} livros que seriam perfeitos para este leitor.
Para cada recomendação, inclua:
1. Título do livro
2. Por que você acha que ele vai gostar
3. Um resumo muito breve

Formate sua resposta de forma clara e entusiasta!"""

            response = self.model.generate_content(prompt)
            recommendations = response.text.strip()

            return {
                'success': True,
                'recommendations': recommendations,
                'error': None
            }

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}", exc_info=True)
            return {
                'success': False,
                'recommendations': None,
                'error': str(e)
            }


# Instância global do serviço (singleton)
_chat_service = None


def get_chat_service():
    """Retorna a instância singleton do serviço de chat."""
    global _chat_service
    if _chat_service is None:
        _chat_service = GeminiChatService()
    return _chat_service

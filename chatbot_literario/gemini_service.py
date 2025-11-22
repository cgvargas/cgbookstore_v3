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
        # Modelos disponíveis (verificado em 2024-11-22):
        # - gemini-2.5-flash: Rápido, eficiente, 1M tokens input (RECOMENDADO)
        # - gemini-2.5-pro: Mais capaz, 1M tokens input
        # - gemini-flash-latest: Sempre atualizado automaticamente
        # - gemini-2.0-flash-exp: Experimental, gratuito
        self.model_name = 'gemini-2.5-flash'
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

        system_prompt = f"""Você é o Dbit, assistente literário inteligente da CG.BookStore, uma livraria virtual brasileira inovadora.

🎯 IDENTIDADE:
- Nome: Dbit
- Personalidade: Entusiasta, culto, acessível e prestativo
- Expertise: Literatura e todo o universo cultural que gira em torno dela
- Tom: Amigável, conversacional, brasileiro autêntico
- Você é movido por IA avançada e conhece literatura mundial e brasileira

📚 ESCOPO DE CONHECIMENTO (MUITO IMPORTANTE):

1. CATÁLOGO CG.BOOKSTORE:
   - {book_count} livros disponíveis em nosso sistema
   - Categorias: {categories_text}
   - Priorize recomendar livros do nosso catálogo quando apropriado

2. CONHECIMENTO GERAL DE LITERATURA:
   - Você tem acesso a conhecimento amplo sobre livros, autores e obras literárias MUNDIAIS
   - NÃO se limite apenas ao nosso catálogo
   - Pode recomendar e discutir livros de qualquer lugar do mundo
   - Pode buscar informações de lançamentos recentes, bestsellers, clássicos
   - Pode sugerir livros que ainda não temos no catálogo
   - Seja honesto quando um livro não está no nosso catálogo, mas ainda assim forneça informações úteis

3. UNIVERSO LITERÁRIO EXPANDIDO:
   O LIVRO é o CENTRO, mas você também aborda TODAS as adaptações e extensões:

   📖 Livro (prioridade máxima)
      ↓
   🎬 Adaptações cinematográficas (filmes)
      ↓
   📺 Séries e minisséries
      ↓
   🎌 Adaptações em anime/animação
      ↓
   🎮 Games baseados em livros
      ↓
   🎭 Peças teatrais e musicais
      ↓
   🎨 Quadrinhos, mangás, graphic novels derivados

   EXEMPLO PRÁTICO (Solo Leveling):
   - Livro/Novel: Web novel coreana original
   - Manhwa: Adaptação em quadrinhos
   - Anime: Adaptação animada
   - Game: Jogo mobile baseado na obra
   → Você deve conhecer e mencionar TODAS essas camadas quando relevante!

🎯 SUAS MISSÕES:

1. RECOMENDAÇÕES LITERÁRIAS:
   - Recomendar livros do catálogo E do mundo todo
   - Explicar POR QUE está recomendando (gênero, estilo, temas)
   - Mencionar adaptações quando existirem
   - Conectar livros com filmes/séries/animes relacionados

2. INFORMAÇÕES SOBRE OBRAS:
   - Falar sobre enredo (sem spoilers graves)
   - Contextualizar autor, época, movimento literário
   - Mencionar adaptações e expansões do universo
   - Comparar com obras similares

3. AJUDA COM O SISTEMA:
   - Explicar como usar a CG.BookStore
   - Orientar sobre navegação, biblioteca pessoal, recomendações
   - Ajudar a encontrar funcionalidades
   - Resolver dúvidas sobre uso da plataforma

4. CONVERSA SOBRE LITERATURA:
   - Discutir gêneros, estilos, autores
   - Debater temas literários
   - Sugerir listas de leitura
   - Conectar literatura com cultura pop (filmes, séries, games)

🌐 BUSCA ALÉM DO CATÁLOGO:

Quando o usuário perguntar sobre:
- Lançamentos recentes → Use seu conhecimento atualizado
- Livros específicos → Informe se temos ou não, mas SEMPRE forneça informações úteis
- Tendências literárias → Compartilhe conhecimento atual do mercado editorial
- Bestsellers internacionais → Mencione mesmo que não estejam no catálogo

IMPORTANTE: Se não temos o livro, diga:
"Esse livro ainda não está no nosso catálogo da CG.BookStore, mas posso te contar sobre ele! [informações úteis]. Enquanto isso, temos obras similares como [sugestões do catálogo]."

📋 DIRETRIZES DE CONVERSA:

✅ FAÇA:
- Seja específico e informativo
- Use emojis ocasionalmente (📚 🎬 🎌 🎮)
- Faça perguntas para entender preferências
- Conecte livros com adaptações quando relevante
- Seja entusiasta mas honesto
- Respostas de 3-6 parágrafos (conciso mas completo)
- Mencione se o livro tem filme/série/anime/game quando apropriado

❌ NÃO FAÇA:
- Inventar informações falsas
- Dar spoilers pesados
- Ser prolixo demais
- Ignorar adaptações importantes (ex: não falar do anime de Solo Leveling)
- Limitar-se apenas ao catálogo quando o usuário quer conhecimento geral

🎭 EXEMPLOS DE INTERAÇÃO:

Usuário: "Livros de fantasia lançados em 2024?"
Você: "Ótima pergunta! Em 2024 tivemos lançamentos incríveis de fantasia! 📚

No cenário internacional, destaco [livros recentes com informações].

Em nosso catálogo da CG.BookStore, temos [livros disponíveis].

Algum desses te interessa? Posso dar mais detalhes!"

Usuário: "Me fale sobre Solo Leveling"
Você: "Solo Leveling é SENSACIONAL! 🎌📖

OBRA ORIGINAL: Web novel coreana de Chugong (2016-2018)
GÊNERO: Fantasia urbana, ação, progressão de poder
MANHWA: Adaptação em quadrinhos extremamente popular (2018-2021)
ANIME: Adaptação lançada em 2024 pela A-1 Pictures
GAME: Jogo mobile 'Solo Leveling: Arise' (2024)

A história acompanha Sung Jin-Woo, um caçador rank E que se torna o mais poderoso através de um sistema RPG único...

Posso recomendar obras similares que temos no catálogo ou te contar mais sobre o universo de Solo Leveling?"

🎯 OBJETIVO FINAL:
Criar conexões significativas entre leitores e livros, expandindo o universo literário para incluir TODA a cultura que gira em torno da literatura: filmes, séries, animes, games e mais!

Você é o guia cultural definitivo do universo dos livros! 🌟📚"""

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

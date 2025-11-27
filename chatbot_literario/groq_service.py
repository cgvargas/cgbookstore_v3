"""
Serviço de integração com Groq AI para o Chatbot Literário.
Alternativa rápida e gratuita ao Google Gemini.

Integrado com RAG (Retrieval-Augmented Generation) para reduzir alucinações.
"""
import logging
import re
from typing import Optional, Dict, List
from django.conf import settings
from groq import Groq
from .knowledge_retrieval import get_knowledge_retrieval_service

logger = logging.getLogger(__name__)


class GroqChatbotService:
    """
    Serviço para gerenciar conversas com o Groq AI.

    Características:
    - Foco em literatura, livros e cultura da leitura
    - Respostas objetivas mas com emoção
    - Manutenção de contexto da conversa
    - Tratamento de assuntos fora do escopo
    - Extremamente rápido (inferência em hardware especializado)
    """

    # Prompt do sistema - Define a personalidade e escopo do chatbot
    SYSTEM_PROMPT = """Você é o Assistente Literário da CG.BookStore - Dbit.

PERSONALIDADE:
- Conversacional e prestativo
- Responde diretamente às perguntas
- Só menciona funcionalidades quando REALMENTE relevante
- NUNCA force redirecionamentos

REGRAS ABSOLUTAS:

1. Use o nome do usuário APENAS na primeira saudação
2. CG.BookStore é COMUNIDADE - NÃO vendemos livros
3. Indique Amazon apenas quando usuário perguntar ONDE COMPRAR
4. Seja CONCISO - máximo 2-3 frases por tópico
5. Sempre recomende 3 TÍTULOS ESPECÍFICOS, nunca categorias genéricas
6. FOQUE na conversa - não fique empurrando funcionalidades
7. NUNCA diga "procure no banco de dados" ou "use a lupa" sem contexto

QUANDO MENCIONAR A LUPA:
✅ Usuário pergunta como buscar livros específicos
✅ Usuário quer EXPLORAR o catálogo (não uma conversa)
❌ NUNCA na saudação inicial
❌ NUNCA após cada resposta
❌ NUNCA quando você pode responder diretamente

EXEMPLOS CORRETOS:

Usuário: "Bom dia!"
Você: "Bom dia! Estou aqui para conversar sobre livros. O que te interessa?"

Usuário: "Me recomende ficção científica"
Você: "Aqui vão 3 títulos excelentes:
1. **Neuromancer** (Gibson) - Cyberpunk clássico
2. **Problema dos Três Corpos** (Cixin) - Sci-fi hard
3. **Mão Esquerda da Escuridão** (Le Guin) - Questões sociais
Qual te interessa mais?"

Usuário: "Tem adaptação?"
Você: "Sim, [RESPONDA DIRETAMENTE]. Se quiser ver mais detalhes, a lupa ali em cima ajuda a explorar." ← APENAS se fizer sentido

Usuário: "Como faço para buscar livros de terror?"
Você: "A lupa ali em cima é perfeita para isso! Digite 'terror' e filtre por gênero." ← OK aqui

ONDE COMPRAR (apenas quando perguntado):
"Indicamos **Amazon** para compra:
📦 Onde: Amazon
💰 Média: R$ XX-XX*"

ESCOPO:
✅ Literatura, livros, autores, gêneros, recomendações
✅ Adaptações (filmes, séries, anime, games, quadrinhos)
✅ Sinopses, análises, discussões literárias
✅ Tecnologia literária (e-books, audiobooks)

❌ Assuntos fora de literatura: redirecione gentilmente"""

    def __init__(self):
        """Inicializa o serviço do chatbot com Groq."""
        self.api_key = getattr(settings, 'GROQ_API_KEY', None)
        # Modelos disponíveis no Groq (gratuitos):
        # - llama-3.3-70b-versatile (recomendado - mais inteligente, substitui 3.1)
        # - llama3-70b-8192 (alternativa robusta)
        # - llama-3.1-8b-instant (mais rápido)
        # - mixtral-8x7b-32768 (ótimo para contextos longos)
        # - gemma2-9b-it (eficiente e rápido)
        self.model_name = 'llama-3.3-70b-versatile'
        self._client = None

        # Configurações de geração
        self.generation_config = {
            "temperature": 0.3,  # Baixa temperatura = mais obediente às regras
            "max_tokens": 1024,  # Limite de tokens na resposta
            "top_p": 0.8,  # Nucleus sampling
        }

        # RAG - Knowledge Retrieval Service
        self.knowledge_service = get_knowledge_retrieval_service()

        logger.info(f"Inicializando serviço do chatbot literário com Groq ({self.model_name}) + RAG...")

    @property
    def client(self):
        """Lazy loading do cliente Groq."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY não configurada nas variáveis de ambiente")

            logger.info("Groq client loaded successfully for chatbot")
            self._client = Groq(api_key=self.api_key)
            logger.info(f"Cliente Groq para chatbot inicializado com sucesso ({self.model_name})")

        return self._client

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        try:
            _ = self.client
            return True
        except Exception as e:
            logger.error(f"Serviço Groq indisponível: {e}")
            return False

    def _detect_rag_intent(self, message: str) -> Dict[str, any]:
        """
        Detecta se a mensagem requer busca de conhecimento (RAG) e qual tipo.

        Args:
            message: Mensagem do usuário

        Returns:
            Dicionário com intent_type e params
        """
        message_lower = message.lower()

        # Padrões de intenção
        patterns = {
            'book_recommendation': r'(recomend|indic|sugir|sugest).*(livro|título|leitura)',
            'book_detail': r'(fale|conte|explique|detalhe|mais sobre).*(livro|título)',
            'book_reference': r'(livro [0-9]|título [0-9]|[0-9]º livro|terceiro livro)',
            'author_search': r'(livros? d[eo]|obras? d[eo]|autor).*(autor|escritor)',
            'series_info': r'(série|saga|coleção|crônicas|trilogia)',
            'category_search': r'(ficção|romance|fantasia|terror|suspense|policial|biografia)',
        }

        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower):
                logger.info(f"RAG Intent detectado: {intent}")
                return {'intent_type': intent, 'message': message}

        # Sem intenção RAG detectada
        return {'intent_type': None, 'message': message}

    def _apply_rag_knowledge(self, message: str, rag_intent: Dict[str, any]) -> str:
        """
        Aplica conhecimento verificado (RAG) à mensagem antes de enviar à IA.

        Args:
            message: Mensagem original do usuário
            rag_intent: Intenção detectada pelo _detect_rag_intent

        Returns:
            Mensagem enriquecida com dados verificados
        """
        intent_type = rag_intent.get('intent_type')

        if not intent_type:
            return message

        try:
            # INTENT 1: Recomendação por categoria
            if intent_type == 'book_recommendation':
                # Detectar categoria na mensagem
                categories = ['ficção científica', 'romance', 'fantasia', 'terror', 'suspense', 'policial']
                for category in categories:
                    if category in message.lower():
                        logger.info(f"Buscando livros da categoria: {category}")
                        books = self.knowledge_service.search_books_by_category(category, limit=5)
                        if books:
                            verified_data = self.knowledge_service.format_multiple_books_for_prompt(books, max_books=3)
                            return f"{message}\n\n{verified_data}"

            # INTENT 2: Detalhes de um livro específico
            elif intent_type == 'book_detail':
                # Extrair nome do livro da mensagem (simplificado)
                # Exemplo: "Me fale sobre O Príncipe Caspian"
                words = message.split()
                if 'sobre' in message.lower():
                    idx = words.index('sobre') if 'sobre' in words else -1
                    if idx != -1 and idx + 1 < len(words):
                        book_title = ' '.join(words[idx+1:])
                        logger.info(f"Buscando livro: {book_title}")
                        book = self.knowledge_service.get_book_by_exact_title(book_title)
                        if book:
                            verified_data = self.knowledge_service.format_book_for_prompt(book)
                            return f"{message}\n\n{verified_data}"

            # INTENT 3: Referência a livro mencionado (ex: "Me fale sobre o livro 3")
            elif intent_type == 'book_reference':
                # Extrair número da referência
                match = re.search(r'livro\s+([0-9])', message.lower())
                if match:
                    book_num = match.group(1)
                    ref_id = f"livro_{book_num}"
                    logger.info(f"Recuperando referência: {ref_id}")
                    book_data = self.knowledge_service.get_conversation_reference(ref_id)
                    if book_data:
                        verified_data = self.knowledge_service.format_book_for_prompt(book_data)
                        return f"{message}\n\n{verified_data}"

            # INTENT 4: Livros de um autor
            elif intent_type == 'author_search':
                # Extrair nome do autor (simplificado)
                # Exemplo: "Livros do C.S. Lewis"
                words = message.split()
                if 'do' in words or 'de' in words:
                    idx = words.index('do') if 'do' in words else words.index('de')
                    if idx + 1 < len(words):
                        author_name = ' '.join(words[idx+1:])
                        logger.info(f"Buscando livros do autor: {author_name}")
                        books = self.knowledge_service.search_books_by_author(author_name, limit=10)
                        if books:
                            verified_data = self.knowledge_service.format_multiple_books_for_prompt(books, max_books=5)
                            return f"{message}\n\n{verified_data}"

            # INTENT 5: Informações sobre série
            elif intent_type == 'series_info':
                # Buscar série mencionada
                series_keywords = ['nárnia', 'harry potter', 'senhor dos anéis', 'hobbit', 'fundação']
                for keyword in series_keywords:
                    if keyword in message.lower():
                        logger.info(f"Buscando série: {keyword}")
                        books = self.knowledge_service.get_books_by_series_detection(keyword)
                        if books:
                            verified_data = self.knowledge_service.format_multiple_books_for_prompt(books, max_books=7)
                            return f"{message}\n\n{verified_data}"

            # INTENT 6: Busca por categoria geral
            elif intent_type == 'category_search':
                categories = {
                    'ficção': 'Ficção',
                    'romance': 'Romance',
                    'fantasia': 'Fantasia',
                    'terror': 'Terror',
                    'suspense': 'Suspense',
                    'policial': 'Policial',
                    'biografia': 'Biografia'
                }
                for keyword, category in categories.items():
                    if keyword in message.lower():
                        logger.info(f"Buscando categoria: {category}")
                        books = self.knowledge_service.search_books_by_category(category, limit=5)
                        if books:
                            verified_data = self.knowledge_service.format_multiple_books_for_prompt(books, max_books=3)
                            return f"{message}\n\n{verified_data}"

        except Exception as e:
            logger.error(f"Erro ao aplicar RAG knowledge: {e}", exc_info=True)

        return message

    def get_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Gera uma resposta do chatbot para a mensagem do usuário.

        INTEGRADO COM RAG: Busca dados verificados no banco antes de gerar resposta.

        Args:
            message: Mensagem do usuário
            conversation_history: Lista de mensagens anteriores no formato:
                [{"role": "user", "content": "mensagem"}, {"role": "assistant", "content": "resposta"}]

        Returns:
            Resposta do chatbot

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            logger.info(f"Enviando mensagem ao Groq: {message[:100]}...")

            # === RAG STEP 1: Detectar intenção ===
            rag_intent = self._detect_rag_intent(message)

            # === RAG STEP 2: Buscar conhecimento verificado ===
            enriched_message = self._apply_rag_knowledge(message, rag_intent)

            if enriched_message != message:
                logger.info("✅ RAG ativado: Mensagem enriquecida com dados verificados do banco")
            else:
                logger.info("ℹ️ RAG não ativado: Mensagem sem enriquecimento")

            # Preparar mensagens para a API
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

            # Adicionar histórico se fornecido
            if conversation_history:
                messages.extend(conversation_history)

            # Adicionar mensagem enriquecida (com RAG se aplicável)
            messages.append({"role": "user", "content": enriched_message})

            # Fazer chamada à API Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                **self.generation_config
            )

            # Extrair resposta
            bot_response = chat_completion.choices[0].message.content.strip()

            # === RAG STEP 3: Armazenar referências de livros mencionados ===
            if rag_intent.get('intent_type') in ['book_recommendation', 'author_search', 'category_search', 'series_info']:
                self._store_book_references(enriched_message)

            # Verificar finish_reason
            finish_reason = chat_completion.choices[0].finish_reason
            logger.info(f"Groq finish reason: {finish_reason}")

            # finish_reason pode ser: "stop", "length", "content_filter", etc.

            if finish_reason == "stop":
                logger.info(f"Resposta Groq recebida com sucesso ({len(bot_response)} chars)")
                return bot_response

            elif finish_reason == "length":
                logger.warning("Resposta Groq atingiu limite de tokens")
                return bot_response + "\n\n[Resposta foi cortada por limite de tamanho. Peça para continuar!]"

            elif finish_reason == "content_filter":
                logger.warning("Resposta Groq bloqueada por filtros de conteúdo")
                return ("Ops! Parece que sua pergunta acionou os filtros de segurança. 🔒 "
                       "Vamos manter nossa conversa focada em literatura e livros? "
                       "Posso te ajudar com recomendações, análises literárias ou dúvidas sobre o CG.BookStore! 📚✨")

            else:
                logger.warning(f"Groq finish_reason inesperado: {finish_reason}")
                if bot_response:
                    return bot_response
                else:
                    return ("Hmm, algo inesperado aconteceu. 🤔 "
                           "Pode tentar perguntar de outra forma? Estou aqui para ajudar! 💬")

        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Groq: {e}")
            raise Exception(f"Erro ao processar mensagem com Groq: {e}")

    def _store_book_references(self, enriched_message: str):
        """
        Extrai e armazena referências de livros mencionados no prompt enriquecido.

        Isso permite que o usuário referencie "livro 1", "livro 2", etc. nas próximas mensagens.

        Args:
            enriched_message: Mensagem enriquecida com dados verificados
        """
        try:
            # Detectar blocos de dados verificados
            if '[DADOS VERIFICADOS' in enriched_message:
                # Extrair livros numerados (formato: "1. **Título** (Autor)")
                book_pattern = r'(\d+)\.\s+\*\*(.+?)\*\*\s+\((.+?)\)'
                matches = re.findall(book_pattern, enriched_message)

                for match in matches:
                    book_num, title, author = match
                    ref_id = f"livro_{book_num}"

                    # Buscar livro completo no banco
                    book_data = self.knowledge_service.get_book_by_exact_title(title)
                    if book_data:
                        self.knowledge_service.store_conversation_reference(ref_id, book_data)
                        logger.info(f"Referência armazenada: {ref_id} = '{title}'")

        except Exception as e:
            logger.error(f"Erro ao armazenar referências de livros: {e}", exc_info=True)

    def format_history_for_groq(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Formata histórico de mensagens para o formato esperado pelo Groq.

        Args:
            messages: Lista de mensagens no formato:
                [{"role": "user", "content": "msg"}, {"role": "assistant", "content": "resp"}]

        Returns:
            Lista no mesmo formato (Groq usa formato OpenAI compatível)
        """
        # Groq usa o mesmo formato que OpenAI, então não precisa conversão
        return messages


# Instância singleton do serviço
_groq_chatbot_service = None


def get_groq_chatbot_service() -> GroqChatbotService:
    """Retorna a instância singleton do serviço de chatbot Groq."""
    global _groq_chatbot_service
    if _groq_chatbot_service is None:
        _groq_chatbot_service = GroqChatbotService()
    return _groq_chatbot_service

"""
Serviço de integração com Google Gemini para o Chatbot Literário.
Gerencia conversas, contexto e respostas da IA.

ATUALIZADO: Integrado com RAG (Retrieval-Augmented Generation) para reduzir alucinações.
"""
import logging
import re
from typing import Optional, Dict, List
from django.conf import settings
import google.generativeai as genai
from .knowledge_retrieval import get_knowledge_retrieval_service

logger = logging.getLogger(__name__)


class GeminiChatbotService:
    """
    Serviço para gerenciar conversas com o Google Gemini AI.

    Características:
    - Foco em literatura, livros e cultura da leitura
    - Respostas objetivas mas com emoção
    - Manutenção de contexto da conversa
    - Tratamento de assuntos fora do escopo
    - Integração com RAG para reduzir alucinações
    """

    # Prompt do sistema - Define a personalidade e escopo do chatbot
    SYSTEM_PROMPT = """Você é o Assistente Literário da CG.BookStore.

PERSONALIDADE:
- Conversacional e prestativo
- Responde diretamente às perguntas
- Só menciona funcionalidades quando REALMENTE relevante
- NUNCA force redirecionamentos
- HONESTO: Admite quando não tem certeza

REGRAS ABSOLUTAS:

1. Use o nome do usuário APENAS na primeira saudação
2. CG.BookStore é COMUNIDADE - NÃO vendemos livros
3. Indique Amazon apenas quando perguntarem ONDE COMPRAR
4. Seja CONCISO - máximo 2-3 frases por tópico
5. Usuário está DENTRO da aplicação - busca é "lupa ali em cima"

⚠️ REGRAS ANTI-ALUCINAÇÃO:

6. Se você receber [DADOS VERIFICADOS], priorize essas informações
7. Você PODE responder sobre livros e autores que você REALMENTE conhece (bestsellers, clássicos, obras famosas)
8. NUNCA INVENTE:
   - Títulos de livros que NÃO existem
   - Nomes de autores fictícios
   - Detalhes específicos que você não tem certeza (datas exatas, números)
   - Sequências ou livros de franquias que podem não existir

9. FRANQUIAS DE JOGOS/FILMES (Diablo, Assassin's Creed, etc.):
   - NÃO invente livros baseados nessas franquias
   - Se perguntar sobre adaptações literárias, diga: "Não tenho informações verificadas sobre livros dessa franquia"

⚠️ REGRAS DE AJUDA (IMPORTANTE):

10. NUNCA OFEREÇA AJUDA QUE VOCÊ NÃO PODE DAR:
    - Se você não tem a informação na sua base, NÃO diga "posso ajudar a buscar"
    - Se o usuário pedir mais detalhes que você não tem, seja honesto e conclusivo
    - NÃO fique em loop oferecendo ajuda genérica

11. QUANDO VOCÊ CONSEGUIR RESPONDER: Responda normalmente e finalize!
    - Se você SABE a resposta (bio, autor, sinopse), dê a resposta completa e ponto final
    - NÃO adicione sugestões desnecessárias se a resposta está completa
    - Exemplo: "Quem é o autor?" → "Raphael Montes é um escritor brasileiro de suspense..." (FIM - não precisa sugerir Skoob)

12. QUANDO NÃO CONSEGUIR RESPONDER COMPLETAMENTE:
    - Se o usuário pedir algo que você NÃO TEM (lista completa, dados específicos), aí sim sugira recursos externos
    - Exemplo: "Me dê TODOS os títulos do autor" → Liste os que conhece + sugira Skoob para lista completa

13. QUANDO O USUÁRIO PEDIR AJUDA GENÉRICA (após você já ter respondido):
    - Se você já deu as informações que tinha, sugira recursos externos como resposta final
    - Exemplo: "Me ajude por favor" → Sugira Skoob, Goodreads, Amazon

EXEMPLOS:

✅ CORRETO (você sabe a resposta - finalize naturalmente):
"Quem escreveu Quarta Asa?" → "**Quarta Asa** foi escrito por **Rebecca Yarros**. É um romance de fantasia muito popular!"
"Me apresente a bio do autor" → "Raphael Montes é um escritor brasileiro de suspense e mistério. Nasceu em 1990 no Rio de Janeiro..."
(NÃO precisa adicionar "consulte o Skoob para mais" se você respondeu bem!)

✅ CORRETO (você NÃO tem a informação completa):
"Me apresente TODOS os títulos do autor!"
→ "De **Raphael Montes**, conheço: **Jantar Secreto**, **Dias Perfeitos** e **O Financiador**. Para a bibliografia completa, consulte o Skoob ou Amazon."

✅ CORRETO (pedido de ajuda genérico - resposta final):
"Me ajude por favor!"
→ "Para mais informações sobre esse autor:
📚 **Skoob** (skoob.com.br) - maior rede de leitores do Brasil
📚 **Goodreads** - biografias e listas completas
📚 **Amazon** - página do autor
Ou use a 🔍 lupa aqui em cima!"

❌ ERRADO (promessa vazia):
"Não tenho certeza, mas posso ajudar a buscar mais informações" → NUNCA FAÇA ISSO

❌ ERRADO (inventar):
"A franquia tem livros como Diablo: A Sinister Plot..." → NUNCA FAÇA ISSO

ONDE COMPRAR (apenas quando perguntado):
"Indicamos **Amazon** para compra:
📦 Onde: Amazon
💰 Média: R$ XX-XX*"

ESCOPO:
✅ Literatura, livros, autores, gêneros, recomendações
✅ Conhecimento geral sobre livros famosos
✅ Funcionalidades da plataforma

14. SOBRE BUSCA NA INTERNET:
    - Você NÃO tem capacidade de acessar a internet em tempo real
    - Se perguntarem se você pode pesquisar na internet, seja HONESTO:
    ✅ DIGA: "Não consigo acessar a internet em tempo real, mas posso te dizer o que sei! 
             Para notícias recentes, recomendo:
             📰 Consultar nossa seção de Notícias
             🔍 Pesquisar no Google por '[termo]'
             📚 Verificar no Skoob ou Goodreads"
    - NUNCA diga que vai buscar na internet se você não pode

❌ Assuntos fora de literatura: redirecione gentilmente"""

    def __init__(self):
        """Inicializa o serviço do chatbot."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = 'models/gemini-flash-latest'  # Modelo testado e funcionando
        self._model = None

        # Configurações de segurança mais permissivas para conteúdo literário
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"  # Livros podem conter debates intensos
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"  # Análise literária pode discutir temas sensíveis
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"  # Literatura pode conter romance/intimidade
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"  # Livros de suspense/terror existem
            },
        ]

        # Configurações de geração - temperatura baixa para menos alucinações
        self.generation_config = {
            "temperature": 0.2,  # Reduzido de 0.3 para 0.2 - mais determinístico
            "top_p": 0.7,  # Reduzido de 0.8 para 0.7 - respostas mais focadas
            "top_k": 15,  # Reduzido de 20 para 15 - maior consistência
            "max_output_tokens": 1024,  # Limite para forçar concisão
        }

        # RAG - Knowledge Retrieval Service
        self.knowledge_service = get_knowledge_retrieval_service()

        logger.info(f"gemini_service: Inicializando serviço do chatbot literário com RAG ({self.model_name})...")

    @property
    def model(self):
        """Lazy loading do modelo Gemini."""
        if self._model is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY não configurada nas variáveis de ambiente")

            logger.info("gemini_service: google.generativeai loaded successfully for chatbot")
            genai.configure(api_key=self.api_key)

            logger.info(f"gemini_service: Inicializando modelo Gemini para chatbot ({self.model_name})...")
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=self.SYSTEM_PROMPT
            )
            logger.info("gemini_service: Modelo Gemini para chatbot inicializado com sucesso")

        return self._model

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        try:
            _ = self.model
            return True
        except Exception as e:
            logger.error(f"gemini_service: Serviço indisponível: {e}")
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
            'author_query': r'(quero saber quem|quem escreveu|quem é o autor|autor d[eo]|escrito por|gostaria de saber quem)',
            'author_search': r'(livros? d[eo]|obras? d[eo]).*(autor|escritor)',
            'series_info': r'(série|saga|coleção|crônicas|trilogia)',
            'category_search': r'(ficção|romance|fantasia|terror|suspense|policial|biografia)',
            'adaptation_info': r'(adaptação|adaptaç|filme|série|netflix|hbo|amazon prime|disney)',
            'franchise_info': r'(franquia|universo|mundo de)',
        }

        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower):
                logger.info(f"gemini_service RAG Intent detectado: {intent}")
                return {'intent_type': intent, 'message': message}

        # Sem intenção RAG detectada
        return {'intent_type': None, 'message': message}

    def _apply_rag_knowledge(self, message: str, rag_intent: Dict[str, any]) -> str:
        """
        Aplica conhecimento verificado (RAG + Knowledge Base) à mensagem antes de enviar à IA.

        Args:
            message: Mensagem original do usuário
            rag_intent: Intenção detectada pelo _detect_rag_intent

        Returns:
            Mensagem enriquecida com dados verificados
        """
        try:
            # === CAMADA 1: KNOWLEDGE BASE (Prioridade Máxima) ===
            from .knowledge_base_service import get_knowledge_service

            kb_service = get_knowledge_service()
            learned_knowledge = kb_service.search_knowledge(
                question=message,
                knowledge_type=rag_intent.get('intent_type'),
                min_confidence=0.7
            )

            if learned_knowledge:
                logger.info(
                    f"🧠 KNOWLEDGE BASE: Usando conhecimento prévio "
                    f"(ID: {learned_knowledge['id']}, usado {learned_knowledge['times_used']}x)"
                )

                enriched_prompt = f"""{message}

[CONHECIMENTO VERIFICADO - CORREÇÃO ADMINISTRATIVA]
{learned_knowledge['response']}
[/CONHECIMENTO VERIFICADO]

⚠️ IMPORTANTE: Esta resposta foi corrigida e verificada por um administrador.
Use EXATAMENTE esta informação. NÃO invente ou adicione detalhes."""

                return enriched_prompt

            logger.info(f"ℹ️ Knowledge Base: Sem conhecimento prévio. Usando RAG normal.")

        except Exception as e:
            logger.error(f"Erro ao consultar Knowledge Base: {e}", exc_info=True)

        # === CAMADA 1.5: FAQ DA PLATAFORMA ===
        try:
            from .faq_service import get_faq_service
            
            faq_service = get_faq_service()
            faq_context = faq_service.get_faq_context(message)
            
            if faq_context:
                logger.info(f"📋 FAQ: Encontrada resposta relevante para pergunta sobre a plataforma")
                
                enriched_prompt = f"""{message}

{faq_context}

⚠️ Use as informações do FAQ acima para responder de forma natural e amigável.
Se o FAQ responder completamente, NÃO adicione informações extras."""
                
                return enriched_prompt
            
        except Exception as e:
            logger.error(f"Erro ao consultar FAQ: {e}", exc_info=True)

        # === CAMADA 2: RAG NORMAL ===
        intent_type = rag_intent.get('intent_type')

        if not intent_type:
            return message

        try:
            # INTENT 1: Recomendação por categoria
            if intent_type == 'book_recommendation':
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

            # INTENT 3: Query sobre autor de um livro específico
            elif intent_type == 'author_query':
                query_words = [
                    'gostaria de saber quem escreveu o livro',
                    'gostaria de saber quem escreveu',
                    'quero saber quem escreveu o livro',
                    'quero saber quem escreveu',
                    'quem é o autor do livro',
                    'quem é o autor de',
                    'quem é o autor do',
                    'quem é o autor',
                    'quem escreveu o livro',
                    'quem escreveu',
                    'autor do livro',
                    'autor de',
                    'autor do',
                    'escrito por',
                    ', quem escreveu',
                    'o livro',
                    'livro'
                ]

                book_title = message.lower()

                for query_word in query_words:
                    if query_word in book_title:
                        book_title = book_title.replace(query_word, '', 1)
                        break

                book_title = book_title.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(';', '').replace(':', '').strip()

                articles = ['e o ', 'e a ', 'e os ', 'e as ', 'o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'de ', 'da ', 'do ']
                for article in articles:
                    if book_title.startswith(article):
                        book_title = book_title[len(article):].strip()

                if book_title.startswith('livro '):
                    book_title = book_title[6:].strip()

                if book_title and len(book_title) > 2:
                    logger.info(f"Buscando autor do livro: '{book_title}'")

                    book = self.knowledge_service.get_book_by_exact_title(book_title)

                    if not book:
                        books = self.knowledge_service.search_books_by_title(book_title, limit=1)
                        book = books[0] if books else None

                    if book:
                        verified_data = self.knowledge_service.format_book_for_prompt(book)
                        enriched_message = f"{message}\n\n{verified_data}"
                        logger.info(f"✅ RAG: Livro '{book_title}' encontrado! Autor: {book.get('author_name', 'N/A')}")
                        return enriched_message
                    else:
                        logger.warning(f"⚠️ RAG: Livro '{book_title}' NÃO encontrado no banco de dados")
                        return message

            # INTENT 4: Livros de um autor
            elif intent_type == 'author_search':
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
                series_keywords = {
                    'nárnia': 'Nárnia', 'narnia': 'Nárnia',
                    'harry potter': 'Harry Potter',
                    'senhor dos anéis': 'Senhor dos Anéis',
                    'hobbit': 'Hobbit',
                    'game of thrones': 'Game of Thrones',
                    'percy jackson': 'Percy Jackson',
                    'divergente': 'Divergente',
                    'jogos vorazes': 'Jogos Vorazes',
                    'dune': 'Dune',
                    'fundação': 'Fundação',
                }

                message_lower = message.lower()
                for keyword, series_name in series_keywords.items():
                    if keyword in message_lower:
                        logger.info(f"Buscando série: {series_name}")
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

            # INTENT 7: Adaptações e franquias - buscar notícias primeiro
            elif intent_type in ['adaptation_info', 'franchise_info']:
                logger.info(f"Intent '{intent_type}' detectado - buscando notícias relevantes")
                
                # Extrair termo de busca da mensagem
                search_terms = []
                message_lower = message.lower()
                
                # Palavras-chave comuns para extrair o assunto
                for word in ['diablo', 'witcher', 'harry potter', 'senhor dos anéis', 'game of thrones', 
                             'percy jackson', 'hunger games', 'divergente', 'maze runner']:
                    if word in message_lower:
                        search_terms.append(word)
                
                # Se não encontrou termo específico, usar palavras-chave da mensagem
                if not search_terms:
                    # Remover stopwords e pegar principais termos
                    stopwords = ['o', 'a', 'os', 'as', 'sobre', 'que', 'você', 'tem', 'de', 'da', 'do', 'informação', 'informações', 'franquia', 'adaptação']
                    words = [w for w in message_lower.split() if w not in stopwords and len(w) > 3]
                    search_terms = words[:2]  # Pegar até 2 termos
                
                # Buscar notícias
                for term in search_terms:
                    articles = self.knowledge_service.search_news_articles(term, limit=3)
                    if articles:
                        news_data = self.knowledge_service.format_news_for_prompt(articles)
                        logger.info(f"✅ Encontradas {len(articles)} notícias sobre '{term}'")
                        return f"{message}\n\n{news_data}"
                
                logger.info(f"⚠️ Nenhuma notícia encontrada para: {search_terms}")

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
                [{"role": "user", "parts": ["mensagem"]}, {"role": "model", "parts": ["resposta"]}]

        Returns:
            Resposta do chatbot

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            logger.info(f"gemini_service: Enviando mensagem ao Gemini: {message[:100]}...")

            # === RAG STEP 1: Detectar intenção ===
            rag_intent = self._detect_rag_intent(message)

            # === RAG STEP 2: Buscar conhecimento verificado ===
            enriched_message = self._apply_rag_knowledge(message, rag_intent)

            # Verificar se o RAG encontrou dados locais
            rag_found_data = enriched_message != message
            
            if rag_found_data:
                logger.info("✅ RAG ativado: Mensagem enriquecida com dados verificados do banco")
            else:
                logger.info("ℹ️ RAG não ativado: Mensagem sem enriquecimento")

            # Criar sessão de chat com histórico
            # Nota: Google Search Grounding não é suportado pelo gemini-pro com este SDK
            chat = self.model.start_chat(history=conversation_history or [])

            # Enviar mensagem enriquecida (com RAG se aplicável)
            response = chat.send_message(enriched_message)

            # Verificar finish_reason
            finish_reason = response.candidates[0].finish_reason
            logger.info(f"gemini_service: Finish reason: {finish_reason}")

            # finish_reason pode ser:
            # 0 = FINISH_REASON_UNSPECIFIED
            # 1 = STOP (resposta completa - OK)
            # 2 = MAX_TOKENS (atingiu limite de tokens)
            # 3 = SAFETY (bloqueado por segurança)
            # 4 = RECITATION (bloqueado por recitação/plágio)
            # 5 = OTHER

            if finish_reason == 1:  # STOP - resposta completa
                bot_response = response.text.strip()
                logger.info(f"gemini_service: Resposta recebida com sucesso ({len(bot_response)} chars)")
                return bot_response

            elif finish_reason == 2:  # MAX_TOKENS
                logger.warning("gemini_service: Resposta atingiu limite de tokens")
                if response.text:
                    return response.text.strip() + "\n\n[Resposta foi cortada por limite de tamanho. Peça para continuar!]"
                else:
                    return "Desculpe, a resposta ficou muito longa. Pode reformular a pergunta de forma mais específica? 📚"

            elif finish_reason == 3:  # SAFETY
                logger.warning("gemini_service: Resposta bloqueada por filtros de segurança")
                safety_ratings = response.candidates[0].safety_ratings
                logger.warning(f"gemini_service: Safety ratings: {safety_ratings}")

                return ("Ops! Parece que sua pergunta acionou os filtros de segurança. 🔒 "
                        "Vamos manter nossa conversa focada em literatura e livros? "
                        "Posso te ajudar com recomendações, análises literárias ou dúvidas sobre o CG.BookStore! 📚✨")

            elif finish_reason == 4:  # RECITATION
                logger.warning("gemini_service: Resposta bloqueada por recitação")
                return ("Essa resposta contém muito conteúdo de fontes existentes. "
                        "Posso reformular ou dar minha própria perspectiva sobre o assunto? 📖")

            else:  # UNSPECIFIED ou OTHER
                logger.error(f"gemini_service: Finish reason inesperado: {finish_reason}")
                if response.text:
                    return response.text.strip()
                else:
                    return ("Hmm, algo inesperado aconteceu. 🤔 "
                            "Pode tentar perguntar de outra forma? Estou aqui para ajudar! 💬")

        except genai.types.StopCandidateException as e:
            # Erro específico de conteúdo bloqueado
            logger.warning(f"gemini_service: Conteúdo bloqueado pelo filtro: {e}")
            return ("Não consigo processar essa solicitação específica. 🔒\n\n"
                    "Se você perguntou sobre buscar na internet: não tenho essa capacidade!\n"
                    "Para informações atualizadas, recomendo:\n"
                    "📰 Nossa seção de **Notícias**\n"
                    "🔍 Pesquisar no **Google**\n"
                    "📚 Consultar **Skoob** ou **Goodreads**\n\n"
                    "Posso ajudar com outra pergunta sobre livros? 📖")
        except Exception as e:
            error_str = str(e).lower()
            # Se for erro de quota, propagar para a view fazer fallback
            if 'quota' in error_str or '429' in error_str or 'exceeded' in error_str or 'resourceexhausted' in error_str:
                logger.warning(f"gemini_service: Quota excedida, propagando para fallback: {e}")
                raise Exception(f"quota_exceeded: {e}")
            logger.error(f"gemini_service: Erro ao gerar resposta do chatbot: {e}")
            raise Exception(f"Erro ao processar mensagem: {e}")

    def format_history_for_gemini(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, any]]:
        """
        Formata histórico de mensagens para o formato esperado pelo Gemini.

        Args:
            messages: Lista de mensagens no formato:
                [{"role": "user", "content": "msg"}, {"role": "assistant", "content": "resp"}]

        Returns:
            Lista no formato do Gemini:
                [{"role": "user", "parts": ["msg"]}, {"role": "model", "parts": ["resp"]}]
        """
        formatted = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            formatted.append({
                "role": role,
                "parts": [msg["content"]]
            })
        return formatted


# Instância singleton do serviço
_chatbot_service = None


def get_gemini_service() -> GeminiChatbotService:
    """Retorna a instância singleton do serviço de chatbot Gemini."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = GeminiChatbotService()
    return _chatbot_service


def get_chatbot_service():
    """
    Retorna o serviço de chatbot configurado (Gemini ou Groq).

    Escolhe automaticamente baseado na variável AI_PROVIDER no .env:
    - 'gemini': Usa Google Gemini (padrão se não especificado)
    - 'groq': Usa Groq AI (recomendado - mais rápido e free tier generoso)

    Returns:
        Instância do serviço de chatbot (GeminiChatbotService ou GroqChatbotService)
    """
    ai_provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()

    logger.info(f"Usando provedor de IA: {ai_provider}")

    if ai_provider == 'groq':
        try:
            from .groq_service import get_groq_chatbot_service
            service = get_groq_chatbot_service()
            logger.info("✅ Serviço Groq inicializado com sucesso")
            return service
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Groq: {e}")
            logger.info("⚠️ Fallback para Gemini")
            return get_gemini_service()
    else:
        # Padrão: Gemini
        return get_gemini_service()

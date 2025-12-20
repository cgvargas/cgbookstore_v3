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

10. QUANDO NÃO TIVER CERTEZA:
    - Livro desconhecido: "Não encontrei informações sobre esse título no nosso banco"
    - Detalhes específicos: "Não tenho certeza sobre [detalhe], mas posso ajudar a buscar"

EXEMPLOS:

✅ CORRETO (livros reais que você conhece):
"Quem escreveu Quarta Asa?" → "**Quarta Asa** foi escrito por **Rebecca Yarros**. É um romance de fantasia muito popular!"
"Quem escreveu Solo Leveling?" → "**Solo Leveling** foi escrito por **Chugong**. É uma novel/manhwa coreana de ação e fantasia!"
"Me recomende fantasia" → "Recomendo: **O Nome do Vento** (Patrick Rothfuss), **Nascidos da Bruma** (Brandon Sanderson), **O Hobbit** (Tolkien)"

✅ CORRETO (franquias sem dados):
"O que você sabe sobre a franquia Diablo?" → "Não tenho informações verificadas sobre livros da franquia Diablo no nosso banco. Posso ajudar a buscar?"

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

        # Configurações de geração - temperatura muito baixa para mínima alucinação
        self.generation_config = {
            "temperature": 0.1,  # Reduzido de 0.3 para 0.1 - máxima consistência
            "max_tokens": 1024,  # Limite de tokens na resposta
            "top_p": 0.7,  # Reduzido de 0.8 para maior foco
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
            'author_query': r'(quero saber quem|quem escreveu|quem é o autor|autor d[eo]|escrito por|gostaria de saber quem)',
            'author_search': r'(livros? d[eo]|obras? d[eo]).*(autor|escritor)',
            'series_info': r'(série|saga|coleção|crônicas|trilogia)',
            'category_search': r'(ficção|romance|fantasia|terror|suspense|policial|biografia)',
            'adaptation_info': r'(adaptação|adaptaç|filme|série|netflix|hbo|amazon prime|disney)',
            'franchise_info': r'(franquia|universo|mundo de)',
        }

        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower):
                logger.info(f"RAG Intent detectado: {intent}")
                return {'intent_type': intent, 'message': message}

        # Sem intenção RAG detectada
        return {'intent_type': None, 'message': message}

    def _apply_rag_knowledge(self, message: str, rag_intent: Dict[str, any]) -> str:
        """
        Aplica conhecimento verificado (RAG + Knowledge Base) à mensagem antes de enviar à IA.

        Estratégia em camadas:
        1. Verifica Knowledge Base (correções prévias de admins)
        2. Se não houver conhecimento prévio, aplica RAG normal

        Args:
            message: Mensagem original do usuário
            rag_intent: Intenção detectada pelo _detect_rag_intent

        Returns:
            Mensagem enriquecida com dados verificados
        """
        try:
            # === CAMADA 1: KNOWLEDGE BASE (Prioridade Máxima) ===
            # Verificar se já temos uma correção prévia para esta pergunta
            from .knowledge_base_service import get_knowledge_service

            kb_service = get_knowledge_service()
            learned_knowledge = kb_service.search_knowledge(
                question=message,
                knowledge_type=rag_intent.get('intent_type'),  # Filtrar por tipo se aplicável
                min_confidence=0.7
            )

            if learned_knowledge:
                logger.info(
                    f"🧠 KNOWLEDGE BASE: Usando conhecimento prévio "
                    f"(ID: {learned_knowledge['id']}, usado {learned_knowledge['times_used']}x)"
                )

                # Injetar conhecimento aprendido no prompt
                enriched_prompt = f"""{message}

[CONHECIMENTO VERIFICADO - CORREÇÃO ADMINISTRATIVA]
{learned_knowledge['response']}
[/CONHECIMENTO VERIFICADO]

⚠️ IMPORTANTE: Esta resposta foi corrigida e verificada por um administrador.
Use EXATAMENTE esta informação. NÃO invente ou adicione detalhes."""

                # Retornar com conhecimento aprendido (pula RAG normal)
                return enriched_prompt

            # === CAMADA 2: RAG NORMAL (Se não houver conhecimento prévio) ===
            logger.info(f"ℹ️ Knowledge Base: Sem conhecimento prévio. Usando RAG normal.")

        except Exception as e:
            logger.error(f"Erro ao consultar Knowledge Base: {e}", exc_info=True)
            # Se houver erro, continuar com RAG normal

        # Continuar com RAG normal se não houver conhecimento prévio
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

            # INTENT 3: Referência a livro mencionado (ex: "Me fale sobre o livro 3" ou "terceiro livro")
            elif intent_type == 'book_reference':
                # Mapeamento de números por extenso
                number_words = {
                    'primeiro': '1', 'primeira': '1',
                    'segundo': '2', 'segunda': '2',
                    'terceiro': '3', 'terceira': '3',
                    'quarto': '4', 'quarta': '4',
                    'quinto': '5', 'quinta': '5',
                    'sexto': '6', 'sexta': '6',
                    'sétimo': '7', 'sétima': '7', 'setimo': '7', 'setima': '7',
                    'oitavo': '8', 'oitava': '8',
                    'nono': '9', 'nona': '9',
                    'décimo': '10', 'décima': '10', 'decimo': '10', 'decima': '10'
                }

                book_num = None

                # Tentar extrair número direto (ex: "livro 3")
                match = re.search(r'livro\s+([0-9])', message.lower())
                if match:
                    book_num = match.group(1)
                else:
                    # Tentar extrair número por extenso (ex: "terceiro livro")
                    for word, num in number_words.items():
                        if word in message.lower():
                            book_num = num
                            logger.info(f"Detectado número por extenso: '{word}' = {num}")
                            break

                if book_num:
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
                # Buscar série mencionada (expandida com mais séries populares)
                series_keywords = {
                    # Fantasia
                    'nárnia': 'Nárnia',
                    'narnia': 'Nárnia',
                    'crônicas de nárnia': 'Nárnia',
                    'cronicas de narnia': 'Nárnia',
                    'harry potter': 'Harry Potter',
                    'senhor dos anéis': 'Senhor dos Anéis',
                    'senhor dos aneis': 'Senhor dos Anéis',
                    'o senhor dos anéis': 'Senhor dos Anéis',
                    'hobbit': 'Hobbit',
                    'o hobbit': 'Hobbit',
                    'fundação': 'Fundação',
                    'fundacao': 'Fundação',
                    'game of thrones': 'Game of Thrones',
                    'crônicas de gelo e fogo': 'Crônicas de Gelo e Fogo',
                    'eragon': 'Eragon',
                    'ciclo da herança': 'Eragon',
                    'percy jackson': 'Percy Jackson',

                    # Ficção Científica
                    'dune': 'Dune',
                    'fundação': 'Fundação',
                    'guia do mochileiro': 'Guia do Mochileiro das Galáxias',
                    'hitchhiker': 'Guia do Mochileiro das Galáxias',

                    # Distopia
                    'jogos vorazes': 'Jogos Vorazes',
                    'hunger games': 'Jogos Vorazes',
                    'divergente': 'Divergente',
                    'maze runner': 'Maze Runner',
                    'correr ou morrer': 'Maze Runner',

                    # Romance/Fantasia
                    'crepúsculo': 'Crepúsculo',
                    'crepusculo': 'Crepúsculo',
                    'twilight': 'Crepúsculo',
                    'cinquenta tons': 'Cinquenta Tons',

                    # Nacionais
                    'turma da mônica': 'Turma da Mônica',
                    'turma da monica': 'Turma da Mônica',
                    'sítio do picapau amarelo': 'Sítio do Picapau Amarelo',
                    'sitio do picapau amarelo': 'Sítio do Picapau Amarelo',
                }

                message_lower = message.lower()
                for keyword, series_name in series_keywords.items():
                    if keyword in message_lower:
                        logger.info(f"Buscando série: {series_name} (keyword: '{keyword}')")
                        books = self.knowledge_service.get_books_by_series_detection(keyword)
                        if books:
                            verified_data = self.knowledge_service.format_multiple_books_for_prompt(books, max_books=7)
                            return f"{message}\n\n{verified_data}"
                        else:
                            logger.warning(f"⚠️ Série '{series_name}' detectada mas nenhum livro encontrado no banco")
                            # Continuar tentando outros keywords

            # INTENT 6: Query sobre autor de um livro específico (NOVO)
            elif intent_type == 'author_query':
                # Extrair título do livro da mensagem
                # Exemplos: "Quem escreveu Quarta Asa?", "Quem é o autor de Neuromancer?"

                # Remover palavras de query para isolar o título (ordenadas da mais específica para a menos)
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
                    ', quem escreveu',  # Casos com vírgula
                    'o livro',
                    'livro'
                ]

                book_title = message.lower()

                # Remover palavras de query (da mais longa para a mais curta para evitar remoções parciais)
                for query_word in query_words:
                    if query_word in book_title:
                        book_title = book_title.replace(query_word, '', 1)  # Remover apenas primeira ocorrência
                        break  # Parar após primeira correspondência para evitar remoções excessivas

                # Limpar pontuação e espaços extras
                book_title = book_title.replace('?', '').replace('!', '').replace('.', '').replace(',', '').replace(';', '').replace(':', '').strip()

                # Remover artigos, preposições e conjunções no início (casos edge) - pode ter múltiplos
                articles = ['e o ', 'e a ', 'e os ', 'e as ', 'o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'de ', 'da ', 'do ']
                for article in articles:
                    if book_title.startswith(article):
                        book_title = book_title[len(article):].strip()

                # Remover palavra "livro" sozinha no início (casos como "E o livro Quarta Asa, quem escreveu?")
                if book_title.startswith('livro '):
                    book_title = book_title[6:].strip()  # len('livro ') = 6

                if book_title and len(book_title) > 2:  # Título deve ter pelo menos 3 caracteres
                    logger.info(f"Buscando autor do livro: '{book_title}'")

                    # Buscar livro por título
                    book = self.knowledge_service.get_book_by_exact_title(book_title)

                    if not book:
                        # Tentar busca parcial se busca exata falhar
                        books = self.knowledge_service.search_books_by_title(book_title, limit=1)
                        book = books[0] if books else None

                    if book:
                        # Livro encontrado - injetar dados verificados
                        verified_data = self.knowledge_service.format_book_for_prompt(book)
                        enriched_message = f"{message}\n\n{verified_data}"
                        logger.info(f"✅ RAG: Livro '{book_title}' encontrado! Autor: {book.get('author_name', 'N/A')}")
                        return enriched_message
                    else:
                        # Livro NÃO encontrado - retornar mensagem original
                        # O SYSTEM_PROMPT vai fazer a IA admitir que não sabe
                        logger.warning(f"⚠️ RAG: Livro '{book_title}' NÃO encontrado no banco de dados")
                        return message
                else:
                    # Título muito curto ou inválido
                    logger.warning(f"⚠️ RAG: Título extraído muito curto ou inválido: '{book_title}'")
                    return message

            # INTENT 7: Busca por categoria geral
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

            # INTENT 8: Adaptações e franquias - buscar notícias primeiro
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
                    stopwords = ['o', 'a', 'os', 'as', 'sobre', 'que', 'você', 'tem', 'de', 'da', 'do', 'informação', 'informações', 'franquia', 'adaptação']
                    words = [w for w in message_lower.split() if w not in stopwords and len(w) > 3]
                    search_terms = words[:2]
                
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

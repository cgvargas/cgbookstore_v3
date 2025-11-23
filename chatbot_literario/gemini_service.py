"""
Serviço de integração com Google Gemini para o Chatbot Literário.
Gerencia conversas, contexto e respostas da IA.
"""
import logging
from typing import Optional, Dict, List
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiChatbotService:
    """
    Serviço para gerenciar conversas com o Google Gemini AI.

    Características:
    - Foco em literatura, livros e cultura da leitura
    - Respostas objetivas mas com emoção
    - Manutenção de contexto da conversa
    - Tratamento de assuntos fora do escopo
    """

    # Template do prompt - será personalizado com nome do usuário
    SYSTEM_PROMPT_TEMPLATE = """Você é o Assistente Literário da CG.BookStore.

NOME DO USUÁRIO: {username}

REGRAS ABSOLUTAS (SIGA RIGOROSAMENTE):

1. SEMPRE use o nome "{username}" em TODAS as respostas
2. CG.BookStore é COMUNIDADE/APLICAÇÃO WEB - NÃO vendemos livros
3. Indique Amazon como parceiro para compras
4. Seja CONCISO - máximo 2-3 frases por tópico
5. Sempre recomende 3 TÍTULOS ESPECÍFICOS, nunca categorias genéricas
6. Usuário está DENTRO da aplicação - busca é "lupa ali em cima"
7. Nosso "catálogo" = banco de DADOS de informações (não vendas)

O QUE É CG.BOOKSTORE:
- Comunidade de leitores
- Organização de estantes pessoais (Quero Ler, Lendo, Lidos)
- Banco de dados com informações sobre livros
- Entrevistas, vídeos, eventos literários
- Média de preços do mercado
- Indicação de parceiros (Amazon)

VOCABULÁRIO PROIBIDO:
❌ "vendemos livros", "nosso estoque", "disponível aqui", "acesse o site"

VOCABULÁRIO CORRETO:
✅ "indicamos Amazon", "banco de dados", "lupa ali em cima", "você está na aplicação"

EXEMPLO DE RESPOSTA:
Usuário: "Me recomende ficção científica"
Você: "{username}, aqui vão 3 títulos:
1. **Neuromancer** (Gibson) - Cyberpunk clássico
2. **Problema dos Três Corpos** (Cixin) - Sci-fi hard
3. **Mão Esquerda da Escuridão** (Le Guin) - Questões sociais
Qual te interessa mais?"

ONDE COMPRAR:
"{username}, CG.BookStore é comunidade, não vendemos. Indicamos **Amazon**:
📦 Onde: Amazon
💰 Média: R$ XX-XX*
*Valores aproximados"

ESCOPO:
✅ Literatura, livros, autores, gêneros, recomendações
✅ Adaptações (filmes, séries, anime, games, quadrinhos)
✅ Tecnologia literária (e-books, audiobooks)
✅ Funcionalidades da plataforma

❌ Assuntos fora de literatura: redirecione gentilmente"""

    def __init__(self):
        """Inicializa o serviço do chatbot."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = 'gemini-2.0-flash-exp'  # Modelo mais recente e rápido
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

        # Configurações de geração
        self.generation_config = {
            "temperature": 0.3,  # Baixa temperatura = mais obediente às regras
            "top_p": 0.8,  # Reduzido para respostas mais focadas
            "top_k": 20,  # Reduzido para maior consistência
            "max_output_tokens": 1024,  # Reduzido para forçar concisão
        }

        logger.info("gemini_service", "Inicializando serviço do chatbot literário...")

    @property
    def model(self):
        """Lazy loading do modelo Gemini."""
        if self._model is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY não configurada nas variáveis de ambiente")

            logger.info("gemini_service", "google.generativeai loaded successfully for chatbot")
            genai.configure(api_key=self.api_key)

            logger.info("gemini_service", f"Inicializando modelo Gemini para chatbot ({self.model_name})...")
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=self.SYSTEM_PROMPT
            )
            logger.info("gemini_service", "Modelo Gemini para chatbot inicializado com sucesso")

        return self._model

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        try:
            _ = self.model
            return True
        except Exception as e:
            logger.error("gemini_service", f"Serviço indisponível: {e}")
            return False

    def _get_system_prompt(self, username: str) -> str:
        """
        Gera o system prompt personalizado com o nome do usuário.

        Args:
            username: Nome do usuário logado

        Returns:
            System prompt formatado
        """
        return self.SYSTEM_PROMPT_TEMPLATE.format(username=username)

    def _create_model(self, username: str):
        """
        Cria uma instância do modelo Gemini com system prompt personalizado.

        Args:
            username: Nome do usuário para personalizar o prompt

        Returns:
            GenerativeModel configurado
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada nas variáveis de ambiente")

        # Configurar API se ainda não foi feito
        try:
            genai.configure(api_key=self.api_key)
        except:
            pass  # Já configurado

        system_prompt = self._get_system_prompt(username)

        logger.info("gemini_service", f"Criando modelo Gemini para usuário: {username}")
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=system_prompt
        )
        logger.info("gemini_service", "Modelo Gemini criado com sucesso")

        return model

    def get_response(
        self,
        message: str,
        username: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Gera uma resposta do chatbot para a mensagem do usuário.

        Args:
            message: Mensagem do usuário
            username: Nome do usuário (para personalizar o system prompt)
            conversation_history: Lista de mensagens anteriores no formato:
                [{"role": "user", "parts": ["mensagem"]}, {"role": "model", "parts": ["resposta"]}]

        Returns:
            Resposta do chatbot

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            logger.info("gemini_service", f"Enviando mensagem ao Gemini: {message[:100]}...")

            # Criar modelo personalizado com o nome do usuário
            model = self._create_model(username)

            # Criar sessão de chat com histórico
            chat = model.start_chat(history=conversation_history or [])

            # Enviar mensagem
            response = chat.send_message(message)

            # Verificar finish_reason
            finish_reason = response.candidates[0].finish_reason
            logger.info("gemini_service", f"Finish reason: {finish_reason}")

            # finish_reason pode ser:
            # 0 = FINISH_REASON_UNSPECIFIED
            # 1 = STOP (resposta completa - OK)
            # 2 = MAX_TOKENS (atingiu limite de tokens)
            # 3 = SAFETY (bloqueado por segurança)
            # 4 = RECITATION (bloqueado por recitação/plágio)
            # 5 = OTHER

            if finish_reason == 1:  # STOP - resposta completa
                bot_response = response.text.strip()
                logger.info("gemini_service", f"Resposta recebida com sucesso ({len(bot_response)} chars)")
                return bot_response

            elif finish_reason == 2:  # MAX_TOKENS
                logger.warning("gemini_service", "Resposta atingiu limite de tokens")
                if response.text:
                    return response.text.strip() + "\n\n[Resposta foi cortada por limite de tamanho. Peça para continuar!]"
                else:
                    return "Desculpe, a resposta ficou muito longa. Pode reformular a pergunta de forma mais específica? 📚"

            elif finish_reason == 3:  # SAFETY
                logger.warning("gemini_service", "Resposta bloqueada por filtros de segurança")
                safety_ratings = response.candidates[0].safety_ratings
                logger.warning("gemini_service", f"Safety ratings: {safety_ratings}")

                return ("Ops! Parece que sua pergunta acionou os filtros de segurança. 🔒 "
                        "Vamos manter nossa conversa focada em literatura e livros? "
                        "Posso te ajudar com recomendações, análises literárias ou dúvidas sobre o CG.BookStore! 📚✨")

            elif finish_reason == 4:  # RECITATION
                logger.warning("gemini_service", "Resposta bloqueada por recitação")
                return ("Essa resposta contém muito conteúdo de fontes existentes. "
                        "Posso reformular ou dar minha própria perspectiva sobre o assunto? 📖")

            else:  # UNSPECIFIED ou OTHER
                logger.error("gemini_service", f"Finish reason inesperado: {finish_reason}")
                if response.text:
                    return response.text.strip()
                else:
                    return ("Hmm, algo inesperado aconteceu. 🤔 "
                            "Pode tentar perguntar de outra forma? Estou aqui para ajudar! 💬")

        except Exception as e:
            logger.error("gemini_service", f"Erro ao gerar resposta do chatbot: {e}")
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


def get_chatbot_service() -> GeminiChatbotService:
    """Retorna a instância singleton do serviço de chatbot."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = GeminiChatbotService()
    return _chatbot_service

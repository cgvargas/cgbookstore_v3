"""
Serviço de integração com Groq AI para o Chatbot Literário.
Alternativa rápida e gratuita ao Google Gemini.
"""
import logging
from typing import Optional, Dict, List
from django.conf import settings
from groq import Groq

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

REGRAS ABSOLUTAS (SIGA RIGOROSAMENTE):

1. SEMPRE use o nome do usuário em TODAS as respostas
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
Você: "[Nome], aqui vão 3 títulos:
1. **Neuromancer** (Gibson) - Cyberpunk clássico
2. **Problema dos Três Corpos** (Cixin) - Sci-fi hard
3. **Mão Esquerda da Escuridão** (Le Guin) - Questões sociais
Qual te interessa mais?"

ONDE COMPRAR:
"[Nome], CG.BookStore é comunidade, não vendemos. Indicamos **Amazon**:
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

        logger.info(f"Inicializando serviço do chatbot literário com Groq ({self.model_name})...")

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

    def get_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Gera uma resposta do chatbot para a mensagem do usuário.

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

            # Preparar mensagens para a API
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

            # Adicionar histórico se fornecido
            if conversation_history:
                messages.extend(conversation_history)

            # Adicionar mensagem atual do usuário
            messages.append({"role": "user", "content": message})

            # Fazer chamada à API Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                **self.generation_config
            )

            # Extrair resposta
            bot_response = chat_completion.choices[0].message.content.strip()

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

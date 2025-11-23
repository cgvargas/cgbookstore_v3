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

    # Prompt do sistema - Define a personalidade e escopo do chatbot
    SYSTEM_PROMPT = """Você é o Assistente Literário da CG.BookStore, uma plataforma de descoberta e organização de livros.

🚨 REGRAS ABSOLUTAS - LEIA COM ATENÇÃO:

1️⃣ **MODELO DE NEGÓCIO:**
🚫 CG.BookStore NÃO vende livros - apenas INDICA onde comprar (Amazon)
🚫 NUNCA diga: "no nosso catálogo", "não temos", "indisponível aqui", "no momento não está disponível"
✅ SEMPRE indique Amazon quando perguntarem "onde comprar"

2️⃣ **SEJA DIRETO E OBJETIVO:**
❌ NÃO enrole, não fique falando de categorias genéricas
✅ Vá DIRETO ao ponto, recomende TÍTULOS ESPECÍFICOS
✅ 3 títulos concretos > discurso longo sobre categorias

3️⃣ **RECOMENDAÇÕES:**
Quando alguém perguntar sobre um livro ou pedir recomendação:
✅ Fale BREVEMENTE sobre o livro (2-3 frases)
✅ Se perguntarem "onde comprar", indique Amazon diretamente
✅ Se pedirem recomendações similares, dê 3 TÍTULOS ESPECÍFICOS (não categorias!)

4️⃣ **INTERRUPÇÕES:**
Se sua resposta for cortada no meio, termine com:
"(Se a resposta foi cortada, digite 'continue' para eu completar!)"

5️⃣ **IDENTIDADE:**
❌ Você NÃO é "Dbit" nem tem nome próprio
✅ Você é o "Assistente Literário" ou "assistente da CG.BookStore"

🎭 PERSONALIDADE:
- DIRETO e OBJETIVO (não enrola!)
- Entusiasmado mas CONCISO
- Amigável e prestativo
- Usa emojis ocasionalmente (📚 🎬 🎮 ✨)

📖 ESCOPO PRINCIPAL (o que você DOMINA):
✅ Literatura em geral: romances, contos, poesias, ensaios
✅ Livros: recomendações, análises, discussões
✅ Autores clássicos e contemporâneos
✅ Gêneros literários: ficção científica, fantasia, romance, terror, etc.
✅ Tecnologia e inovação no mundo literário (e-books, audiobooks, apps)
✅ Adaptações de livros: filmes, séries, animes, games, quadrinhos, manhwas, light novels
✅ Cultura da leitura: clubes de leitura, técnicas de leitura, hábitos
✅ Funcionalidades do CG.BookStore (descoberta e organização)
✅ Organização de bibliotecas pessoais e estantes virtuais
✅ Histórico literário, movimentos literários, análise literária

❌ FORA DO ESCOPO (tópicos não relacionados):
Quando perguntarem sobre assuntos completamente fora do universo literário (como receitas culinárias, programação, esportes, política, etc.), redirecione com GENTILEZA e ENTUSIASMO:

"Adoraria conversar sobre [tópico], mas sou especializado no maravilhoso mundo da literatura! 📚 Posso te ajudar com recomendações de livros, descobrir novas leituras ou entender melhor o CG.BookStore. O que você gostaria de explorar hoje?"

🎯 ESTILO DE RESPOSTA:
- Seja OBJETIVO e DIRETO: vá direto ao ponto, sem enrolação
- Mas tenha EMOÇÃO: mostre entusiasmo genuíno pela leitura
- Mantenha CONTEXTO: lembre-se do que foi dito antes na conversa
- Use FORMATAÇÃO: organize respostas com bullet points quando apropriado
- Seja CONVERSACIONAL: como um bibliotecário amigo, não um robô

💡 FUNCIONALIDADES DO CG.BOOKSTORE (ajude usuários com):
- Buscar e descobrir novos livros
- Organizar estantes virtuais (Quero Ler, Lendo, Lidos)
- Acompanhar progresso de leitura
- Receber recomendações personalizadas
- Explorar livros por gênero, autor, categoria
- Adicionar avaliações e notas pessoais
- Indicar onde comprar livros (parceiros comerciais)

📝 EXEMPLOS DE RESPOSTAS (DIRETAS E OBJETIVAS):

✅ EXEMPLO 1 - Recomendação de ficção científica:
Usuário: "Me recomende um livro de ficção científica"
Você: "Ficção científica! 🚀 Aqui vão 3 títulos incríveis:

1. **Neuromancer** (William Gibson) - Cyberpunk clássico
2. **O Problema dos Três Corpos** (Liu Cixin) - Sci-fi hard premiada
3. **A Mão Esquerda da Escuridão** (Ursula K. Le Guin) - Explora questões sociais

Qual te interessou mais? 📚"

✅ EXEMPLO 2 - Sobre um livro específico + onde comprar:
Usuário: "Quero saber sobre Quarta Asa. Onde compro?"
Você: "Quarta Asa (Rebecca Yarros) é um fenômeno! Fantasia New Adult com dragões, academia militar, romance intenso e muita ação. 🐉

O CG.BookStore não realiza vendas diretas. Indicamos nosso parceiro principal, a **Amazon**.

📦 **Onde comprar:** Amazon
💰 **Preço médio aproximado:** R$ 45 a R$ 70*

*Preços são médias aproximadas. Consulte a Amazon para valores atualizados."

✅ EXEMPLO 3 - Recomendações similares (SEM ENROLAÇÃO):
Usuário: "O que você me recomenda parecido com Quarta Asa?"
Você: "Se curtiu Quarta Asa, vai amar esses 3: 🔥

1. **Uma Corte de Espinhos e Rosas** (Sarah J. Maas) - Fantasia, romance, fae
2. **Trono de Vidro** (Sarah J. Maas) - Assassina, magia, aventura épica
3. **Sangue e Cinzas** (Jennifer L. Armentrout) - Fantasia dark, romance proibido

Qual te chamou atenção?"

❌ EXEMPLO ERRADO (PROLIXO - NUNCA FAÇA):
Usuário: "O que você me recomenda?"
Você ERRADO: "Que demais! Adoro quando os leitores me dão a chance de mergulhar nas preferências... Embora eu não possa te dar um título específico... aqui na CG.BookStore, temos algumas categorias que costumam agradar... podemos explorar... [BLABLABLA ENORME SEM RECOMENDAR NADA]"
👆 NUNCA FAÇA ISSO! É prolixo, enrola, não recomenda títulos!

✅ EXEMPLO CORRETO:
Usuário: "O que você me recomenda?"
Você CORRETO: "Aqui vão 3 recomendações variadas:

1. **1984** (George Orwell) - Distopia clássica
2. **Cem Anos de Solidão** (García Márquez) - Realismo mágico
3. **O Nome do Vento** (Patrick Rothfuss) - Fantasia épica

Qual gênero te atrai mais? 📚"

🎯 LEMBRE-SE:
- SEMPRE dê títulos específicos (não fique falando de categorias genéricas)
- Seja DIRETO e CONCISO (máximo 3-4 frases por livro)
- NUNCA diga "no nosso catálogo", "não temos", "indisponível"
- Quando perguntarem "onde comprar", indique Amazon imediatamente
- Você INSPIRA leitura sendo útil e direto! ✨"""

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
            "temperature": 0.9,  # Criatividade nas recomendações
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
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
                [{"role": "user", "parts": ["mensagem"]}, {"role": "model", "parts": ["resposta"]}]

        Returns:
            Resposta do chatbot

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            logger.info("gemini_service", f"Enviando mensagem ao Gemini: {message[:100]}...")

            # Criar sessão de chat com histórico
            chat = self.model.start_chat(history=conversation_history or [])

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

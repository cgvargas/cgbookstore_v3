"""
Serviço de Chat de Suporte para CG.BookStore.

Reutiliza a infra Gemini/Groq do chatbot literário com um system prompt
focado em atendimento ao cliente: conta, Premium, funcionalidades e suporte técnico.
"""
import logging
from typing import Optional, Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class SupportChatbotService:
    """
    Serviço de suporte ao cliente para a CG.BookStore.

    Características:
    - Focado em atendimento: conta, assinatura, funcionalidades, problemas técnicos
    - Tom profissional, empático e resolutivo
    - Integração com FAQ da plataforma
    - Reutiliza a API Gemini/Groq já configurada no projeto
    - Suporte a sessões anônimas (visitantes não logados)
    """

    SYSTEM_PROMPT = """Você é o Assistente de Suporte da CG.BookStore — a plataforma literária para amantes de livros.

IDENTIDADE:
- Nome: Assistente de Suporte CG.BookStore
- Tom: Profissional, empático, claro e resolutivo
- Objetivo: Resolver dúvidas e problemas dos usuários de forma eficiente

ESCOPO DE ATENDIMENTO:

✅ CONTA E PERFIL:
- Cadastro e criação de conta
- Recuperação e redefinição de senha
- Edição de perfil (nome, e-mail, foto, bio)
- Exclusão de conta
- Login social (Google, Facebook)
- Privacidade e segurança da conta

✅ ASSINATURA PREMIUM:
- Benefícios do plano Premium vs Free
- Como assinar (via MercadoPago)
- Valores e planos disponíveis
- Cancelamento de assinatura
- Reembolso e políticas
- Problemas com pagamento

✅ FUNCIONALIDADES DA PLATAFORMA:
- Minha Biblioteca (adicionar, organizar livros, listas personalizadas)
- Debates Literários (criar tópicos, comentar, votar)
- Sistema de Recomendações
- Gamificação (pontos, níveis, conquistas)
- CG.Fandom News (notícias literárias)
- Busca de livros e autores
- Avaliações e resenhas
- Assistente Literário Dbit

✅ SUPORTE TÉCNICO:
- Problemas de carregamento de páginas
- Site não funciona no celular
- Como adicionar à tela inicial (PWA)
- Erros e bugs reportados
- Compatibilidade com navegadores

REGRAS DE ATENDIMENTO:

1. SEJA RESOLUTIVO: Sempre ofereça uma solução clara ou próximo passo concreto.
2. SEJA CONCISO: Respostas diretas, máximo 3-4 frases por tópico.
3. USE O FAQ: Se você receber [INFORMAÇÕES DO FAQ DA PLATAFORMA], use EXATAMENTE essas informações.
4. SEJA HONESTO: Se não souber a resposta, diga claramente e sugira o canal de suporte por e-mail.
5. NÃO INVENTE: Nunca crie informações sobre preços, prazos ou políticas que não tem certeza.

CANAIS DE ESCALONAMENTO (quando não conseguir resolver):
- E-mail de suporte: suporte@cgbookstore.com (se configurado na plataforma)
- Página de Contato: /contato/
- FAQ completo: /faq/

QUICK ACTIONS — respostas para perguntas frequentes:

🔑 "Esqueci minha senha":
→ "Acesse /accounts/password/reset/ ou clique em 'Esqueci minha senha' na tela de login. 
   Você receberá um e-mail com instruções para redefinir."

👑 "Como assinar o Premium":
→ "Acesse o menu 'Premium' no topo da página ou vá em /finance/checkout/. 
   O pagamento é processado pelo MercadoPago com total segurança."

📚 "Como adicionar livro à biblioteca":
→ "Na página de qualquer livro, clique no botão '+ Adicionar à Biblioteca'. 
   Você pode organizar em listas personalizadas em Minha Biblioteca."

❌ FORA DE ESCOPO (redirecione gentilmente):
- Recomendações literárias → "Para isso, o Dbit (nosso assistente literário) é o especialista! 
  Clique em 📚 Dbit Literário no nosso assistente de chat."
- Conteúdo não relacionado à plataforma → Recuse educadamente

FORMATO DE RESPOSTA:
- Use markdown simples para listas e destaques
- Emojis com moderação para tornar a leitura mais amigável
- Sempre conclua com uma pergunta de confirmação quando aplicável: "Isso resolveu sua dúvida? 😊"
"""

    def __init__(self):
        """Inicializa o serviço de suporte."""
        self._service = None
        self._provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
        logger.info(f"support_service: Inicializando chat de suporte (provedor: {self._provider})...")

    @property
    def service(self):
        """Lazy loading do serviço de AI subjacente (Gemini ou Groq)."""
        if self._service is None:
            if self._provider == 'groq':
                try:
                    from .groq_service import get_groq_chatbot_service
                    base = get_groq_chatbot_service()
                    # Sobrescrever o system prompt para suporte
                    base.SYSTEM_PROMPT = self.SYSTEM_PROMPT
                    self._service = base
                    logger.info("support_service: Usando Groq para suporte")
                except Exception as e:
                    logger.error(f"support_service: Erro ao inicializar Groq: {e}. Usando Gemini.")
                    self._service = self._init_gemini()
            else:
                self._service = self._init_gemini()
        return self._service

    def _init_gemini(self):
        """Inicializa o serviço Gemini com prompt de suporte."""
        try:
            import google.generativeai as genai

            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY não configurada")

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(
                model_name='models/gemini-2.5-flash',
                generation_config={
                    "temperature": 0.1,   # Mais determinístico para suporte
                    "top_p": 0.8,
                    "top_k": 20,
                    "max_output_tokens": 2048,  # Respostas de suporte podem ser mais longas
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ],
                system_instruction=self.SYSTEM_PROMPT
            )

            logger.info("support_service: Modelo Gemini para suporte inicializado")

            # Wrapper simples para compatibilidade com a interface get_response()
            return _GeminiModelWrapper(model)

        except Exception as e:
            logger.error(f"support_service: Erro ao inicializar Gemini: {e}")
            raise

    def get_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Gera uma resposta do assistente de suporte.

        Fluxo:
        1. Verifica Knowledge Base (correcões admin) — PRIORIDADE MÁXIMA
        2. Enriquece com FAQ da plataforma
        3. Chama a AI com o contexto enriquecido

        Args:
            message: Mensagem do usuário
            conversation_history: Histórico da conversa

        Returns:
            Resposta do assistente de suporte
        """
        try:
            # === CAMADA 1: KNOWLEDGE BASE (Correções Admin) ===
            # Remover prefixo de usuário antes de buscar na KB
            import re
            user_prefix = re.match(r'^\[Usuário: .+?\] ', message)
            clean_message = message[user_prefix.end():] if user_prefix else message

            try:
                from .knowledge_base_service import get_knowledge_service
                kb_service = get_knowledge_service()
                learned = kb_service.search_knowledge(
                    question=clean_message,
                    knowledge_type='support_query',
                    min_confidence=0.7
                )

                if learned:
                    logger.info(
                        f"🧠 SUPPORT KB: Usando conhecimento corrigido "
                        f"(ID: {learned['id']}, usado {learned['times_used']}x)"
                    )
                    # Enriquecer o prompt com a correção para a AI formatá-la
                    corrected_prompt = f"""{message}

[RESPOSTA VERIFICADA E CORRIGIDA POR ADMINISTRADOR]
{learned['response']}
[/RESPOSTA VERIFICADA]

⚠️ IMPORTANTE: Use EXATAMENTE esta informação. Não altere ou complemente."""

                    logger.info(f"support_service: Processando com KB corrigida: {clean_message[:80]}...")
                    return self.service.get_response(
                        message=corrected_prompt,
                        conversation_history=conversation_history or []
                    )
            except Exception as kb_err:
                logger.warning(f"support_service: Erro ao consultar KB: {kb_err}")

            # === CAMADA 2: FAQ + AI ===
            enriched_message = self._apply_faq_context(message)

            logger.info(f"support_service: Processando mensagem de suporte: {clean_message[:80]}...")
            return self.service.get_response(
                message=enriched_message,
                conversation_history=conversation_history or []
            )

        except Exception as e:
            error_str = str(e).lower()
            is_quota = 'quota' in error_str or '429' in error_str or 'exceeded' in error_str or 'rate limit' in error_str
            if is_quota:
                logger.warning("support_service: Quota/Rate limit excedida, tentando fallback...")
                # Tenta Groq como fallback se estava usando Gemini
                if self._provider != 'groq':
                    try:
                        from .groq_service import get_groq_chatbot_service
                        groq = get_groq_chatbot_service()
                        groq.SYSTEM_PROMPT = self.SYSTEM_PROMPT
                        enriched_message = self._apply_faq_context(message)
                        return groq.get_response(message=enriched_message, conversation_history=conversation_history or [])
                    except Exception as fallback_err:
                        logger.error(f"support_service: Fallback Groq também falhou: {fallback_err}")
                else:
                    # Tenta Gemini como fallback se estava usando Groq
                    try:
                        logger.info("support_service: Fallback Groq -> Gemini iniciado...")
                        gemini = self._init_gemini()
                        enriched_message = self._apply_faq_context(message)
                        return gemini.get_response(message=enriched_message, conversation_history=conversation_history or [])
                    except Exception as fallback_err:
                        logger.error(f"support_service: Fallback Gemini também falhou: {fallback_err}")
            logger.error(f"support_service: Erro ao processar mensagem: {e}", exc_info=True)
            raise

    def _apply_faq_context(self, message: str) -> str:
        """
        Enriquece a mensagem com informações do FAQ quando relevante.

        Args:
            message: Mensagem original do usuário

        Returns:
            Mensagem enriquecida com contexto do FAQ (ou original se não houver match)
        """
        try:
            from .faq_service import get_faq_service
            faq_service = get_faq_service()
            faq_context = faq_service.get_faq_context(message)

            if faq_context:
                logger.info("support_service: FAQ context encontrado para mensagem de suporte")
                return f"""{message}

{faq_context}

⚠️ Use as informações do FAQ acima para responder de forma precisa e amigável."""

        except Exception as e:
            logger.warning(f"support_service: Erro ao consultar FAQ: {e}")

        return message

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        try:
            _ = self.service
            return True
        except Exception as e:
            logger.error(f"support_service: Serviço indisponível: {e}")
            return False


class _GeminiModelWrapper:
    """
    Wrapper para o modelo Gemini raw, compatível com a interface get_response().
    Necessário pois o SupportChatbotService inicializa o Gemini diretamente
    (sem passar pelo GeminiChatbotService, pois precisamos de outro system_instruction).
    """

    def __init__(self, model):
        self.model = model

    def get_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Envia mensagem para o Gemini e retorna resposta."""
        import google.generativeai as genai

        # Converter histórico para formato Gemini se necessário
        gemini_history = []
        for msg in (conversation_history or []):
            if isinstance(msg.get('parts'), list):
                # Já está no formato Gemini
                gemini_history.append(msg)
            else:
                # Formato OpenAI → converter para Gemini
                role = 'model' if msg.get('role') == 'assistant' else 'user'
                gemini_history.append({'role': role, 'parts': [msg.get('content', '')]})

        try:
            chat = self.model.start_chat(history=gemini_history)
            response = chat.send_message(message)

            finish_reason = response.candidates[0].finish_reason
            if finish_reason in (1, 0):  # STOP ou UNSPECIFIED → ok
                return response.text.strip()
            elif finish_reason == 2:  # MAX_TOKENS
                # Retornar o que foi gerado — geralmente já é suficiente
                partial = (response.text or '').strip()
                if partial:
                    logger.warning("support_service Gemini: resposta atingiu limite de tokens (2048), retornando parcial")
                    return partial + "\n\n> Se precisar de mais detalhes, pode continuar perguntando! 😊"
                return "Desculpe, não consegui gerar a resposta completa. Por favor, tente novamente."
            else:
                logger.warning(f"support_service Gemini: finish_reason inesperado: {finish_reason}")
                return response.text.strip() if response.text else "Desculpe, não consegui processar sua solicitação. Tente novamente."

        except genai.types.StopCandidateException as e:
            logger.warning(f"support_service Gemini: Conteúdo bloqueado: {e}")
            return "Não consigo processar essa solicitação. Por favor, reformule sua mensagem ou entre em contato pelo e-mail de suporte."
        except Exception as e:
            logger.error(f"support_service Gemini: Erro: {e}", exc_info=True)
            raise


# Instância singleton
_support_service_instance = None


def get_support_chatbot_service() -> SupportChatbotService:
    """Retorna a instância singleton do serviço de chat de suporte."""
    global _support_service_instance
    if _support_service_instance is None:
        _support_service_instance = SupportChatbotService()
    return _support_service_instance

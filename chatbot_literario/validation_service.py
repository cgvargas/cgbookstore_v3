"""
Serviço de Validação Cruzada (Cross-Validation) de IA em tempo real.
Utiliza uma segunda IA (ex: Groq Llama se o principal for Gemini) para revisar
e auto-corrigir possíveis alucinações literárias antes de exibir ao usuário.
"""
import logging
from django.conf import settings
from .gemini_service import get_gemini_service
from .groq_service import get_groq_chatbot_service

logger = logging.getLogger(__name__)


def validate_and_correct_response(user_message: str, draft_response: str) -> tuple:
    """
    Valida a resposta gerada pelo provedor de IA principal usando o provedor secundário.
    Corrige alucinações ou erros factuais literários em tempo real.

    Args:
        user_message: Mensagem original do usuário.
        draft_response: Resposta provisória gerada pela IA principal.

    Returns:
        tuple: (response_text, was_corrected)
    """
    # 1. Verificar se a validação cruzada está ativada nas configurações
    if not getattr(settings, 'AI_CROSS_VALIDATION_ENABLED', True):
        return draft_response, False

    primary_provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()

    # Se o provedor secundário for o mesmo ou não estiver configurado corretamente, aborta
    if primary_provider == 'gemini':
        validator_provider = 'groq'
    else:
        validator_provider = 'gemini'

    logger.info(f"🔍 Validação Cruzada: Iniciando validação com o provedor secundário '{validator_provider}'")

    try:
        # Configurar prompt de validação
        prompt = f"""Você é um validador de fatos literários de alta precisão.
Sua missão é detectar erros factuais e alucinações nas respostas geradas por outro modelo de IA sobre livros, autores e dados literários.

PERGUNTA DO USUÁRIO: "{user_message}"
RESPOSTA DO OUTRO MODELO: "{draft_response}"

ANÁLISE DE ALUCINAÇÕES E ERROS DE FATO:
Analise se a resposta do outro modelo contém erros factuais, tais como:
1. Ordem incorreta de livros em séries/trilogias (ex: dizer que "O Temor do Sábio" é o primeiro da trilogia "A Crônica do Assassino do Rei", quando na verdade é o segundo).
2. Títulos de livros inventados que não existem (ex: "As Histórias Perdidas de Vintas").
3. Autores errados atribuídos a livros.
4. Outros erros factuais claros sobre literatura (datas de publicação erradas, sinopses erradas, etc.).

REGRAS DE RETORNO:
- Se a resposta estiver 100% CORRETA factualmente e não contiver alucinações, responda APENAS e EXATAMENTE com a palavra: APROVADO
- Se você detectar QUALQUER erro de fato, reescreva a resposta por completo, corrigindo os erros. O seu retorno deve ser DIRETAMENTE o texto final corrigido que será enviado ao usuário. Não inclua introduções, notas, metadiscussões ou explicações como "a resposta do outro modelo contém erros" ou "resposta corrigida:". Escreva como se você fosse o próprio chatbot literário respondendo ao usuário final de forma direta, correta e polida. Mantenha o mesmo tom e estilo do rascunho original.
"""

        # 2. Chamar o provedor secundário
        if validator_provider == 'groq':
            # Validador é o Groq
            groq_service = get_groq_chatbot_service()
            if not groq_service.is_available():
                logger.warning("⚠️ Validador Groq indisponível, ignorando validação")
                return draft_response, False

            validation_response = groq_service.get_response(message=prompt, conversation_history=[])
        else:
            # Validador é o Gemini
            gemini_service = get_gemini_service()
            if not gemini_service.is_available():
                logger.warning("⚠️ Validador Gemini indisponível, ignorando validação")
                return draft_response, False

            validation_response = gemini_service.get_response(message=prompt, conversation_history=[])

        validation_response = validation_response.strip()

        # 3. Analisar a resposta do validador
        validation_response_clean = validation_response.strip().lower().replace('.', '').replace('"', '').replace("'", "")
        draft_response_clean = draft_response.strip().lower().replace('.', '').replace('"', '').replace("'", "")

        if "aprovado" in validation_response.lower() or validation_response == "APROVADO" or validation_response_clean == draft_response_clean:
            logger.info("✅ Validação Cruzada: Resposta aprovada sem alterações.")
            return draft_response, False
        else:
            logger.warning(
                f"⚠️ Validação Cruzada: ERRO DETECTADO. Resposta corrigida de:\n"
                f"'{draft_response}'\npara:\n'{validation_response}'"
            )
            return validation_response, True

    except Exception as err:
        logger.error(f"❌ Erro ao executar a validação cruzada da IA: {err}", exc_info=True)
        # Em caso de falha na validação, retornar a resposta original para não indisponibilizar o serviço
        return draft_response, False

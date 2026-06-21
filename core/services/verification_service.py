"""
Serviço de verificação por IA usando o Google Gemini Multimodal ou Groq Vision.
Valida se a foto de uma página física de um livro coincide com o livro lido.
"""
import json
import logging
import base64
from typing import Dict, Any, Optional
import PIL.Image
from django.conf import settings
import google.generativeai as genai
from groq import Groq

logger = logging.getLogger(__name__)


def verify_reading_page_with_gemini(
    image_file_path: Any,
    book_title: str,
    book_author: str,
    isbn: Optional[str],
    page_number: int
) -> Dict[str, Any]:
    """
    Tenta usar o Groq Llama 3.2 Vision (gratuito) se configurado,
    caso contrário faz fallback para o Gemini 2.5 Flash.

    Args:
        image_file_path: Caminho local ou objeto de arquivo da imagem
        book_title: Título do livro
        book_author: Nome do autor
        isbn: Código ISBN do livro
        page_number: Número da página solicitada

    Returns:
        dict: {'is_valid': bool, 'confidence': float, 'reason': str}
    """
    ai_provider = getattr(settings, 'AI_PROVIDER', 'groq')
    groq_key = getattr(settings, 'GROQ_API_KEY', None)
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)

    # 1. Priorizar Groq Vision se configurado
    if ai_provider == 'groq' and groq_key:
        logger.info("verification_service: Usando Groq Vision (llama-3.2-11b-vision-preview)")
        try:
            # Carregar os bytes da imagem
            if hasattr(image_file_path, 'read'):
                image_file_path.seek(0)
                image_bytes = image_file_path.read()
            else:
                with open(image_file_path, 'rb') as f:
                    image_bytes = f.read()

            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Chamar o cliente Groq
            client = Groq(api_key=groq_key)
            prompt = f"""
            Você é um auditor imparcial e detalhista do sistema de gamificação literária do CG.BookStore.
            Sua função é verificar se a foto enviada pelo usuário é de fato a página física real do livro que ele alega ter lido, para evitar trapaças no ranking competitivo.

            DADOS DA SOLICITAÇÃO:
            - Livro: "{book_title}"
            - Autor: "{book_author}"
            - ISBN informado: "{isbn or 'Não informado'}"
            - Página que deve estar na foto: Página {page_number}

            INSTRUÇÕES DE ANÁLISE:
            1. A imagem anexada deve conter a foto de uma página impressa de um livro físico ou e-reader.
            2. Analise o texto legível e o contexto literário. Este texto pertence ao livro "{book_title}" de "{book_author}"?
            3. Procure por indicadores do número da página (número impresso no rodapé ou cabeçalho). É a página {page_number} ou muito próxima (devido a layout de capítulo)?
            4. Se a imagem não for de um livro (ex: objetos genéricos, fotos pretas, prints de tela sem texto), marque imediatamente como inválido.

            Responda ESTRITAMENTE em formato JSON (sem blocos de código markdown, apenas o JSON bruto contendo as chaves 'is_valid', 'confidence' e 'reason'):
            {{
              "is_valid": true ou false,
              "confidence": valor decimal de 0.0 a 1.0,
              "reason": "Sua explicação detalhada do veredito."
            }}
            """

            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            response_text = response.choices[0].message.content.strip()
            logger.info(f"verification_service: Resposta do Groq recebida: {response_text}")

            result = json.loads(response_text)
            return {
                'is_valid': bool(result.get('is_valid', False)),
                'confidence': float(result.get('confidence', 0.0)),
                'reason': str(result.get('reason', 'Nenhuma justificativa fornecida.'))
            }
        except Exception as e:
            logger.warning(f"verification_service: Falha ao validar com o Groq: {e}. Fazendo fallback para o Gemini.")

    # 2. Fallback para o Gemini
    if not gemini_key:
        logger.error("verification_service: Nenhuma chave de API configurada (Groq/Gemini).")
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': "Serviços de verificação por IA indisponíveis no momento."
        }

    try:
        # Carregar a imagem para o PIL
        if hasattr(image_file_path, 'read'):
            image_file_path.seek(0)
            img = PIL.Image.open(image_file_path)
        else:
            img = PIL.Image.open(image_file_path)
    except Exception as e:
        logger.error(f"verification_service: Erro ao abrir a imagem com PIL: {e}")
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': f"Não foi possível abrir o arquivo de imagem enviado: {str(e)}"
        }

    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Você é um auditor imparcial e detalhista do sistema de gamificação literária do CG.BookStore.
        Sua função é verificar se a foto enviada pelo usuário é de fato a página física real do livro que ele alega ter lido, para evitar trapaças no ranking competitivo.

        DADOS DA SOLICITAÇÃO:
        - Livro: "{book_title}"
        - Autor: "{book_author}"
        - ISBN informado: "{isbn or 'Não informado'}"
        - Página que deve estar na foto: Página {page_number}

        INSTRUÇÕES DE ANÁLISE:
        1. A imagem anexada deve conter a foto de uma página impressa de um livro físico ou e-reader.
        2. Analise o texto legível e o contexto literário. Este texto pertence ao livro "{book_title}" de "{book_author}"?
        3. Procure por indicadores do número da página (número impresso no rodapé ou cabeçalho). É a página {page_number} ou muito próxima (devido a layout de capítulo)?
        4. Se a imagem não for de um livro (ex: objetos genéricos, fotos pretas, prints de tela sem texto), marque imediatamente como inválido.

        Responda ESTRITAMENTE em formato JSON (sem blocos de código adicionais, apenas o JSON bruto contendo as chaves 'is_valid', 'confidence' e 'reason'):
        {{
          "is_valid": true ou false,
          "confidence": valor decimal de 0.0 a 1.0,
          "reason": "Sua explicação detalhada do veredito."
        }}
        """

        logger.info(f"verification_service: Chamando Gemini para validar livro '{book_title}' (Pág. {page_number})")
        response = model.generate_content(
            [prompt, img],
            generation_config={"response_mime_type": "application/json"}
        )

        response_text = response.text.strip()
        logger.info(f"verification_service: Resposta do Gemini recebida: {response_text}")

        result = json.loads(response_text)
        return {
            'is_valid': bool(result.get('is_valid', False)),
            'confidence': float(result.get('confidence', 0.0)),
            'reason': str(result.get('reason', 'Nenhuma justificativa fornecida.'))
        }

    except json.JSONDecodeError as e:
        logger.error(f"verification_service: Erro ao decodificar JSON retornado pelo Gemini: {e}")
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': "A IA não retornou um formato de resposta válido. Por favor, tente enviar a foto novamente."
        }
    except Exception as e:
        logger.error(f"verification_service: Erro geral no Gemini: {e}", exc_info=True)
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': f"Erro de comunicação com o serviço de verificação por IA: {str(e)}"
        }

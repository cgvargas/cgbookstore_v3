"""
Serviço de IA para auxiliar administrativo na extração de metadados de livros.
Utiliza Google Gemini com saída JSON estruturada.
"""

import json
import re
import requests
import logging
from django.conf import settings
import google.generativeai as genai
from core.models import Author, Category

logger = logging.getLogger(__name__)


class AIBookAssistantService:
    """Serviço para extração de informações de livros com múltiplos modelos e contingência."""

    GEMINI_MODELS = [
        'gemini-2.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-3.5-flash',
        'gemini-3.7-flash',
        'gemini-flash-latest',
    ]

    def __init__(self):
        self.gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)

    def is_available(self) -> bool:
        """Verifica se alguma chave de IA ou serviço está disponível."""
        return bool(
            self.gemini_key or 
            getattr(settings, 'GROQ_API_KEY', '') or 
            getattr(settings, 'OPENROUTER_API_KEY', '')
        )

    def _get_amazon_url(self, isbn: str) -> str:
        """Retorna a URL do livro na Amazon baseada no ISBN (convertendo para ISBN-10 se possível)."""
        if not isbn:
            return ""
        clean = re.sub(r'[\-\s]', '', isbn)
        if len(clean) == 13 and clean.startswith('978'):
            nine_digits = clean[3:12]
            total = 0
            for i, digit in enumerate(nine_digits):
                total += int(digit) * (10 - i)
            remainder = total % 11
            check_digit = 11 - remainder
            if check_digit == 10:
                check_digit = 'X'
            elif check_digit == 11:
                check_digit = '0'
            asin = f"{nine_digits}{check_digit}"
        else:
            asin = clean
        return f"https://www.amazon.com.br/dp/{asin}"

    def _download_temp_cover(self, cover_url: str, isbn: str) -> dict:
        """
        Baixa a imagem da capa e salva temporariamente no media storage (Supabase/R2/Local).
        Retorna um dicionário com o path relativo e a URL pública.
        """
        if not cover_url:
            return {}
        import os
        import uuid
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        try:
            filename = f"temp_{isbn or uuid.uuid4().hex}.jpg"
            relative_path = f"books/covers/{filename}"
            
            logger.info("Baixando imagem de capa temporária de %s para o media storage", cover_url)
            r = requests.get(cover_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                saved_path = default_storage.save(
                    relative_path,
                    ContentFile(r.content)
                )
                public_url = default_storage.url(saved_path)
                logger.info("Capa temporária salva no storage em: %s (URL: %s)", saved_path, public_url)
                return {
                    'path': saved_path,
                    'url': public_url
                }
        except Exception as e:
            logger.error("Erro ao baixar imagem de capa temporária: %s", e)
        return {}

    def _fetch_isbn_metadata(self, text_content: str) -> dict:
        """Busca metadados do livro pelo ISBN em APIs externas com fallback."""
        if not text_content:
            return {}

        # Procurar por padrões de ISBN-10 ou ISBN-13
        isbn_pattern = re.compile(
            r'\b(?:ISBN(?:-1[03])?:?\s*)?([0-9xX](?:[0-9xX\-\s]{8,15})[0-9xX])\b',
            re.IGNORECASE
        )
        match = isbn_pattern.search(text_content)
        if not match:
            return {}

        raw_isbn = match.group(1)
        cleaned_isbn = re.sub(r'[\-\s]', '', raw_isbn)

        if len(cleaned_isbn) not in (10, 13):
            return {}

        # 1. Tentar Open Library via HTTP (rápido, sem limites, evita timeouts)
        try:
            url = f"http://openlibrary.org/api/books?bibkeys=ISBN:{cleaned_isbn}&format=json&jscmd=data"
            logger.info("Buscando ISBN %s no Open Library via HTTP...", cleaned_isbn)
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                key = f"ISBN:{cleaned_isbn}"
                if key in data:
                    book_info = data[key]
                    cover_url = book_info.get("cover", {}).get("large") or book_info.get("cover", {}).get("medium")
                    temp_cover_info = self._download_temp_cover(cover_url, cleaned_isbn)
                    
                    metadata = {
                        "title": book_info.get("title"),
                        "subtitle": book_info.get("subtitle", ""),
                        "publisher": book_info.get("publishers", [{}])[0].get("name", "") if book_info.get("publishers") else "",
                        "page_count": book_info.get("number_of_pages"),
                        "author_name": book_info.get("authors", [{}])[0].get("name", "") if book_info.get("authors") else "",
                        "publish_date": book_info.get("publish_date"),
                        "isbn": cleaned_isbn,
                        "temp_cover_image": temp_cover_info.get('path') if temp_cover_info else None,
                        "temp_cover_url": temp_cover_info.get('url') if temp_cover_info else None,
                        "source": "Open Library"
                    }
                    logger.info("Dados obtidos com sucesso do Open Library: %s", metadata)
                    return metadata
        except Exception as e:
            logger.error("Erro ao buscar ISBN %s no Open Library: %s", cleaned_isbn, e)

        # 2. Tentar Google Books API como fallback
        try:
            from core.utils.google_books_api import search_books
            logger.info("Buscando ISBN %s no Google Books como fallback...", cleaned_isbn)
            res_data = search_books(isbn=cleaned_isbn)
            if 'books' in res_data and len(res_data['books']) > 0:
                book_info = res_data['books'][0]
                cover_url = book_info.get("thumbnail")
                temp_cover_info = self._download_temp_cover(cover_url, cleaned_isbn)
                
                metadata = {
                    "title": book_info.get("title"),
                    "subtitle": book_info.get("subtitle", ""),
                    "publisher": book_info.get("publisher", ""),
                    "page_count": book_info.get("page_count"),
                    "author_name": book_info.get("authors", [""])[0] if book_info.get("authors") else "",
                    "publish_date": book_info.get("published_date"),
                    "isbn": cleaned_isbn,
                    "temp_cover_image": temp_cover_info.get('path') if temp_cover_info else None,
                    "temp_cover_url": temp_cover_info.get('url') if temp_cover_info else None,
                    "average_rating": book_info.get("average_rating"),
                    "ratings_count": book_info.get("ratings_count"),
                    "source": "Google Books"
                }
                logger.info("Dados obtidos com sucesso do Google Books: %s", metadata)
                return metadata
        except Exception as e:
            logger.error("Erro ao buscar ISBN %s no Google Books: %s", cleaned_isbn, e)

        return {}

    def _build_data_from_isbn(self, isbn_data: dict, text_content: str = None) -> dict:
        """Constrói um payload estruturado diretamente dos metadados de ISBN quando a IA falha."""
        title = isbn_data.get('title') or ''
        author = isbn_data.get('author_name') or ''
        isbn = isbn_data.get('isbn') or ''
        
        # Formatar data
        pub_date = isbn_data.get('publish_date')
        formatted_date = None
        if pub_date:
            year_match = re.search(r'\b(19\d\d|20\d\d)\b', str(pub_date))
            if year_match:
                formatted_date = f"{year_match.group(1)}-01-01"

        data = {
            "title": title,
            "subtitle": isbn_data.get('subtitle') or '',
            "description": f"Sinopse e detalhes de '{title}' ({author}). Metadados importados automaticamente via {isbn_data.get('source', 'ISBN')}.",
            "publication_date": formatted_date,
            "isbn": isbn,
            "publisher": isbn_data.get('publisher') or '',
            "price": 49.90,
            "page_count": isbn_data.get('page_count'),
            "language": "pt",
            "available_print": True,
            "available_kindle": True,
            "available_audiobook": False,
            "available_pdf": False,
            "author_name": author,
            "author_bio": f"Autor(a) de {title}." if author else "",
            "category_name": "Literatura Geral",
            "average_rating": isbn_data.get('average_rating') or 4.5,
            "ratings_count": isbn_data.get('ratings_count') or 10,
            "purchase_partner_name": "Amazon Brasil",
            "purchase_partner_url": self._get_amazon_url(isbn) if isbn else "",
            "temp_cover_image": isbn_data.get('temp_cover_image'),
            "temp_cover_url": isbn_data.get('temp_cover_url'),
            "_degraded_notice": "Metadados obtidos diretamente de fontes públicas (Open Library/Google Books). A IA está temporariamente em cooldown."
        }
        return data

    def _clean_json_response(self, text: str) -> dict:
        """Limpa blocos de código e decodifica texto JSON."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1)
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "", 1)
        
        # Procurar primeiro '{' e último '}'
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
            
        return json.loads(cleaned.strip())

    def _enrich_and_map_database_entities(self, extracted_data: dict, isbn_data: dict) -> dict:
        """Enriquece dados com capas, ratings e IDs de Autor/Categoria locais."""
        # Mapear capa e avaliações do ISBN
        if isbn_data:
            if 'temp_cover_image' in isbn_data and isbn_data['temp_cover_image']:
                extracted_data['temp_cover_image'] = isbn_data['temp_cover_image']
            if 'temp_cover_url' in isbn_data and isbn_data['temp_cover_url']:
                extracted_data['temp_cover_url'] = isbn_data['temp_cover_url']
            
            if isbn_data.get('average_rating') is not None and extracted_data.get('average_rating') in (None, 0.0, 0):
                extracted_data['average_rating'] = isbn_data.get('average_rating')
            if isbn_data.get('ratings_count') is not None and extracted_data.get('ratings_count') in (None, 0):
                extracted_data['ratings_count'] = isbn_data.get('ratings_count')

        # Garantir casting
        try:
            extracted_data['average_rating'] = float(extracted_data.get('average_rating', 0.0) or 0.0)
        except (ValueError, TypeError):
            extracted_data['average_rating'] = 4.5

        try:
            extracted_data['ratings_count'] = int(extracted_data.get('ratings_count', 0) or 0)
        except (ValueError, TypeError):
            extracted_data['ratings_count'] = 10

        try:
            extracted_data['price'] = float(extracted_data.get('price', 0.0) or 0.0)
            if extracted_data['price'] <= 0.0:
                extracted_data['price'] = 49.90
        except (ValueError, TypeError):
            extracted_data['price'] = 49.90

        # Amazon URL
        isbn_val = extracted_data.get('isbn')
        if isbn_val:
            clean_isbn = re.sub(r'[\-\s]', '', isbn_val)
            if len(clean_isbn) in (10, 13):
                extracted_data['purchase_partner_name'] = 'Amazon Brasil'
                partner_url = extracted_data.get('purchase_partner_url', '')
                if not partner_url or 'amazon' not in partner_url.lower() or partner_url.endswith('.com') or partner_url.endswith('.com/'):
                    extracted_data['purchase_partner_url'] = self._get_amazon_url(clean_isbn)

        # Mapear Autor e Categoria no banco local
        author_name = str(extracted_data.get('author_name', '') or '').strip()
        category_name = str(extracted_data.get('category_name', '') or '').strip()

        author_id = None
        category_id = None

        if author_name:
            author_obj = Author.objects.filter(name__iexact=author_name).first()
            if not author_obj:
                author_obj = Author.objects.filter(name__icontains=author_name).first()
            if author_obj:
                author_id = author_obj.id
                extracted_data['author_name'] = author_obj.name

        if category_name:
            category_obj = Category.objects.filter(name__iexact=category_name).first()
            if not category_obj:
                category_obj = Category.objects.filter(name__icontains=category_name).first()
            if not category_obj:
                first_word = category_name.split()[0]
                if len(first_word) >= 3:
                    category_obj = Category.objects.filter(name__icontains=first_word).first()
            
            if category_obj:
                category_id = category_obj.id
                extracted_data['category_name'] = category_obj.name

        extracted_data['author_id'] = author_id
        extracted_data['category_id'] = category_id

        return extracted_data

    def analyze_book_data(self, text_content: str = None, file_path: str = None, mime_type: str = None) -> dict:
        """
        Analisa texto e/ou um arquivo para extrair dados estruturados do livro.
        Possui cascata multi-modelo Gemini, fallback para Groq/OpenRouter e fallback determinístico via ISBN.
        """
        if not self.is_available():
            raise ValueError("Nenhum serviço de IA configurado no arquivo .env.")

        # 1. Buscar metadados externos deterministicamente se houver ISBN no texto
        isbn_data = self._fetch_isbn_metadata(text_content)

        # Se houver arquivo de imagem físico, salvar temporariamente
        if file_path and mime_type and mime_type.startswith('image/'):
            try:
                import uuid
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                
                isbn_for_file = isbn_data.get('isbn') if isbn_data else None
                if not isbn_for_file:
                    isbn_pattern = re.compile(r'\b(?:ISBN(?:-1[03])?:?\s*)?([0-9xX]{10,13})\b', re.IGNORECASE)
                    match = isbn_pattern.search(text_content or '')
                    isbn_for_file = match.group(1) if match else uuid.uuid4().hex
                
                filename = f"temp_upload_{isbn_for_file}.jpg"
                relative_path = f"books/covers/{filename}"
                
                if not default_storage.exists(relative_path):
                    with open(file_path, 'rb') as f:
                        saved_path = default_storage.save(relative_path, ContentFile(f.read()))
                    public_url = default_storage.url(saved_path)
                    
                    if not isbn_data:
                        isbn_data = {}
                    isbn_data['temp_cover_image'] = saved_path
                    isbn_data['temp_cover_url'] = public_url
                    logger.info("Imagem de upload copiada com sucesso para capa temporária: %s", saved_path)
            except Exception as e:
                logger.error("Erro ao copiar imagem de upload para capa temporária: %s", e)

        prompt = """
        Você é um auxiliar administrativo especialista encarregado de extrair e pesquisar informações detalhadas sobre livros na internet com FIDELIDADE ABSOLUTA.

        [FONTE PRIMÁRIA DE PESQUISA & REGRAS ANTI-ALUCINAÇÃO]:
        Priorize buscar informações na AMAZON BRASIL (amazon.com.br) e na sinopse oficial da editora.
        
        ⚠️ REGRA CRÍTICA PARA PERSONAGENS E TRAMAS:
        NUNCA invente ou inverta o papel de personagens (ex: nunca confunda antagônicos/vilões com aliados ou amigos do protagonista).
        Se você não tiver certeza absoluta sobre a função exata de um personagem secundário, limite-se a transcrever fielmente a sinopse oficial publicada pela editora na Amazon Brasil.

        [REGRA CRÍTICA PARA ISBN]:
        Se for fornecida uma seção de [DADOS DE REFERÊNCIA OBTIDOS PELO ISBN NA WEB], os valores ali contidos (como título, autor, editora, isbn, quantidade de páginas) são a VERDADE ABSOLUTA. Você DEVE usar exatamente os valores dessa seção para preencher os respectivos campos (title, author_name, publisher, isbn, page_count).

        Sua resposta deve ser estritamente em formato JSON, sem blocos de código markdown (NÃO use ```json ou ```). A resposta deve conter as seguintes chaves e formatos exatos:
        
        - title: Título principal do livro (string).
        - subtitle: Subtítulo do livro (string, ou string vazia "" se não houver).
        - description: Sinopse ou descrição detalhada do livro em português exatamente como na editora (string).
        - publication_date: Data de publicação no formato YYYY-MM-DD. Se apenas o ano for conhecido, use YYYY-01-01. Se a data for inválida ou desconhecida, retorne null.
        - isbn: Código ISBN (10 ou 13 dígitos) contendo apenas dígitos e hífens.
        - publisher: Nome da editora (string, ou string vazia "" se desconhecido).
        - price: Preço médio estimado de mercado na Amazon Brasil em reais (float). NÃO retorne null nem 0. Ex: 49.90.
        - page_count: Número de páginas (inteiro ou null).
        - language: Código ISO 639-1 de idioma (ex: 'pt', 'en', 'es', 'fr').
        - available_print: true se houver indicação de versão física/impressa, caso contrário false.
        - available_kindle: true se houver indicação de e-book ou Kindle, caso contrário false.
        - available_audiobook: true se houver indicação de audiolivro, caso contrário false.
        - available_pdf: true se houver indicação de formato PDF, caso contrário false.
        - author_name: Nome do autor principal do livro (string).
        - author_bio: Biografia ou resumo resumido sobre a vida e obra do autor principal em português (string, ou string vazia "" se desconhecido).
        - category_name: Categoria ou gênero principal do livro (ex: Fantasia, Ficção Científica, Romance, Biografia, Manga, HQ, Terror, Suspense, Autoajuda, Tecnologia) (string).
        - average_rating: Avaliação média do livro de 0.00 a 5.00 (float).
        - ratings_count: Número total estimado de avaliações (inteiro).
        - purchase_partner_name: 'Amazon Brasil' ou 'Amazon'.
        - purchase_partner_url: Link completo do livro na Amazon Brasil (string).
        """

        uploaded_file = None
        extracted_data = None
        last_error = None

        # 2. Tentar modelos Gemini em cascata
        if self.gemini_key:
            contents = [prompt]
            if file_path:
                try:
                    logger.info("Enviando arquivo temporário para API do Gemini: %s (%s)", file_path, mime_type)
                    uploaded_file = genai.upload_file(path=file_path, mime_type=mime_type)
                    contents.append(uploaded_file)
                except Exception as up_err:
                    logger.warning("Falha ao subir arquivo para Gemini Files API: %s", up_err)

            if isbn_data:
                contents.append(f"\n[DADOS DE REFERÊNCIA OBTIDOS PELO ISBN NA WEB]:\n{json.dumps(isbn_data, ensure_ascii=False)}")

            if text_content:
                contents.append(f"\nDados ou texto adicional do usuário:\n{text_content}")

            for model_name in self.GEMINI_MODELS:
                try:
                    logger.info("Chamando Gemini (%s) para extração de metadados...", model_name)
                    model_inst = genai.GenerativeModel(model_name=model_name)
                    response = model_inst.generate_content(
                        contents,
                        generation_config={
                            "response_mime_type": "application/json",
                            "temperature": 0.0,
                            "top_p": 0.1,
                        },
                        request_options={"timeout": 10.0}
                    )

                    response_text = response.text.strip()
                    extracted_data = self._clean_json_response(response_text)
                    logger.info("✅ Extração com Gemini (%s) bem-sucedida!", model_name)
                    break
                except Exception as gem_err:
                    err_str = str(gem_err).lower()
                    last_error = gem_err
                    is_quota = 'quota' in err_str or '429' in err_str or 'exceeded' in err_str or 'resourceexhausted' in err_str or '504' in err_str
                    if is_quota:
                        logger.warning("⚠️ Gemini quota/timeout no modelo %s. Tentando próximo modelo...", model_name)
                        continue
                    else:
                        logger.warning("⚠️ Erro no modelo %s: %s", model_name, gem_err)
                        continue

        # 3. Fallback para Groq ou OpenRouter (quando sem arquivo ou se Gemini falhou)
        if not extracted_data and text_content:
            from core.services.ai_provider_service import AIProviderFactory
            for provider_name in ['groq', 'openrouter']:
                try:
                    provider = AIProviderFactory.get_provider(provider_name)
                    if provider and getattr(provider, 'api_key', ''):
                        logger.info("Tentando contingência de extração com %s...", provider_name)
                        full_prompt = f"{prompt}\n\n[DADOS DE REFERÊNCIA]:\n{json.dumps(isbn_data or {}, ensure_ascii=False)}\n\n[TEXTO DO USUÁRIO]:\n{text_content}"
                        resp_text = provider.generate_text(
                            prompt=full_prompt,
                            system_instruction="Você é um assistente que extrai dados de livros estritamente em formato JSON.",
                            feature_name="admin_ai_assistant",
                            temperature=0.1
                        )
                        extracted_data = self._clean_json_response(resp_text)
                        logger.info("✅ Extração com %s bem-sucedida!", provider_name)
                        break
                except Exception as prov_err:
                    logger.warning("⚠️ Fallback para %s falhou: %s", provider_name, prov_err)
                    last_error = prov_err
                    continue

        # 4. Fallback Determinístico Inteligente via ISBN
        if not extracted_data and isbn_data:
            logger.info("ℹ️ Todas as IAs indisponíveis. Usando fallback determinístico via metadados de ISBN.")
            extracted_data = self._build_data_from_isbn(isbn_data, text_content)

        # Limpar arquivo temporário da API do Gemini
        if uploaded_file:
            try:
                uploaded_file.delete()
            except Exception as e:
                logger.warning("Falha ao remover arquivo temporário do Gemini: %s", e)

        # Se ainda não houver dados extraídos, lançar erro humanizado
        if not extracted_data:
            err_msg = str(last_error or 'Serviço de IA indisponível')
            if '429' in err_msg or 'quota' in err_msg.lower() or 'exceeded' in err_msg.lower():
                raise Exception("Limite temporário de requisições de IA atingido. Por favor, aguarde alguns instantes e tente novamente.")
            raise Exception(f"Não foi possível processar os dados: {err_msg}")

        # 5. Enriquecer e mapear entidades do banco de dados
        return self._enrich_and_map_database_entities(extracted_data, isbn_data)

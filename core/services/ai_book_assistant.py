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
    """Serviço para extração de informações de livros usando Google Gemini."""

    def __init__(self):
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        if gemini_key:
            genai.configure(api_key=gemini_key)
            from google.ai.generativelanguage_v1beta import Tool
            google_search_tool = Tool(google_search={})
            self.model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                tools=[google_search_tool]
            )
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY não configurada nas configurações do Django.")

    def is_available(self) -> bool:
        """Verifica se a chave da API do Gemini está disponível."""
        return self.model is not None

    def _get_isbn_10(self, isbn: str) -> str:
        """Retorna o ISBN-10 a partir de um ISBN-13 ou do próprio ISBN-10."""
        if not isbn:
            return None
        clean = re.sub(r'[\-\s]', '', isbn)
        if len(clean) == 10:
            return clean
        if len(clean) == 13 and clean.startswith('978'):
            nine_digits = clean[3:12]
            total = 0
            for i, digit in enumerate(nine_digits):
                total += int(digit) * (10 - i)
            remainder = total % 11
            check_val = 11 - remainder
            if check_val == 10:
                check_digit = 'X'
            elif check_val == 11:
                check_digit = '0'
            else:
                check_digit = str(check_val)
            return nine_digits + check_digit
        return None

    def _download_temp_cover(self, cover_url: str, isbn: str) -> str:
        """Baixa a imagem da capa e salva temporariamente no diretório de media."""
        if not cover_url:
            return None
        import os
        import uuid
        from django.conf import settings
        
        try:
            filename = f"temp_{isbn or uuid.uuid4().hex}.jpg"
            relative_path = os.path.join("books", "covers", filename)
            # Normalizar para barras normais do Django/Unix
            relative_path = relative_path.replace('\\', '/')
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            logger.info("Baixando imagem de capa temporária de %s para %s", cover_url, full_path)
            r = requests.get(cover_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(full_path, 'wb') as f:
                    f.write(r.content)
                return relative_path
        except Exception as e:
            logger.error("Erro ao baixar imagem de capa temporária: %s", e)
        return None

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
                    temp_cover = self._download_temp_cover(cover_url, cleaned_isbn)
                    
                    metadata = {
                        "title": book_info.get("title"),
                        "subtitle": book_info.get("subtitle", ""),
                        "publisher": book_info.get("publishers", [{}])[0].get("name", "") if book_info.get("publishers") else "",
                        "page_count": book_info.get("number_of_pages"),
                        "author_name": book_info.get("authors", [{}])[0].get("name", "") if book_info.get("authors") else "",
                        "publish_date": book_info.get("publish_date"),
                        "isbn": cleaned_isbn,
                        "temp_cover_image": temp_cover,
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
                temp_cover = self._download_temp_cover(cover_url, cleaned_isbn)
                
                metadata = {
                    "title": book_info.get("title"),
                    "subtitle": book_info.get("subtitle", ""),
                    "publisher": book_info.get("publisher", ""),
                    "page_count": book_info.get("page_count"),
                    "author_name": book_info.get("authors", [""])[0] if book_info.get("authors") else "",
                    "publish_date": book_info.get("published_date"),
                    "isbn": cleaned_isbn,
                    "temp_cover_image": temp_cover,
                    "average_rating": book_info.get("average_rating"),
                    "ratings_count": book_info.get("ratings_count"),
                    "source": "Google Books"
                }
                logger.info("Dados obtidos com sucesso do Google Books: %s", metadata)
                return metadata
        except Exception as e:
            logger.error("Erro ao buscar ISBN %s no Google Books: %s", cleaned_isbn, e)

        return {}

    def analyze_book_data(self, text_content: str = None, file_path: str = None, mime_type: str = None) -> dict:
        """
        Analisa texto e/ou um arquivo para extrair dados estruturados do livro.
        
        Args:
            text_content: Texto copiado, sinopse ou prompt digitado pelo administrador.
            file_path: Caminho local para o arquivo (imagem ou PDF) carregado temporariamente.
            mime_type: Tipo MIME do arquivo (ex: 'application/pdf', 'image/jpeg').
            
        Returns:
            Dicionário com os campos estruturados do livro.
        """
        if not self.is_available():
            raise ValueError(
                "Serviço de IA indisponível. Por favor, adicione a chave GEMINI_API_KEY no arquivo .env."
            )

        # Buscar metadados externos deterministicamente se houver ISBN no texto
        isbn_data = self._fetch_isbn_metadata(text_content)

        prompt = """
        Você é um auxiliar administrativo experiente encarregado de extrair e pesquisar informações detalhadas sobre livros na internet ou a partir dos dados fornecidos (texto, imagens ou documentos).
        
        Você tem acesso à ferramenta de busca do Google (Google Search). Utilize-a ativamente para buscar e confirmar informações em sites como Google Books, Amazon, Skoob, editoras e outras fontes literárias confiáveis sempre que:
        1. O usuário fornecer apenas o título, autor ou ISBN parciais (ex: "pesquise o livro X").
        2. Faltarem dados importantes como ISBN, data de publicação, quantidade de páginas, editora ou preço de mercado.
        3. For necessário obter uma sinopse completa e correta em português.

        [REGRA CRÍTICA PARA ISBN]:
        Se for fornecida uma seção de [DADOS DE REFERÊNCIA OBTIDOS PELO ISBN NA WEB], os valores ali contidos (como título, autor, editora, isbn, quantidade de páginas) são a VERDADE ABSOLUTA. Você DEVE usar exatamente os valores dessa seção para preencher os respectivos campos (title, author_name, publisher, isbn, page_count) para evitar qualquer alucinação do nome do livro associado ao ISBN. Use as ferramentas de busca ou seu próprio conhecimento para traduzir, buscar a sinopse em português ('description') e preencher os demais campos.

        Sua resposta deve ser estritamente em formato JSON, sem blocos de código markdown (NÃO use ```json ou ```). A resposta deve conter as seguintes chaves e formatos exatos:
        
        - title: Título principal do livro (string).
        - subtitle: Subtítulo do livro (string, ou string vazia "" se não houver).
        - description: Sinopse ou descrição detalhada do livro em português (string).
        - publication_date: Data de publicação no formato YYYY-MM-DD. Se apenas o ano for conhecido, use YYYY-01-01. Se a data for inválida ou desconhecida, retorne null.
        - isbn: Código ISBN (10 ou 13 dígitos) contendo apenas dígitos e hífens.
        - publisher: Nome da editora (string, ou string vazia "" se desconhecido).
        - price: Preço médio estimado de mercado em reais (float ou null).
        - page_count: Número de páginas (inteiro ou null).
        - language: Código ISO 639-1 de idioma (ex: 'pt', 'en', 'es', 'fr').
        - available_print: true se houver qualquer indicação de versão física/impressa, caso contrário false.
        - available_kindle: true se houver indicação de e-book ou Kindle, caso contrário false.
        - available_audiobook: true se houver indicação de audiolivro, caso contrário false.
        - available_pdf: true se houver indicação de formato PDF, caso contrário false.
        - author_name: Nome do autor principal do livro (string).
        - category_name: Categoria ou gênero principal do livro (ex: Fantasia, Ficção Científica, Romance, Biografia) (string).
        - average_rating: Avaliação média do livro de 0.00 a 5.00 (float ou null). Se não souber por fontes externas, estime com base no sucesso crítico global da obra.
        - ratings_count: Número total estimado de avaliações (inteiro ou null). Se não souber por fontes externas, estime baseado no alcance do livro.
        - purchase_partner_name: "Amazon" (defina sempre como "Amazon").

        Preencha o máximo de campos que puder extrair ou pesquisar com alto grau de confiança.
        """

        contents = [prompt]
        uploaded_file = None

        try:
            # Se um arquivo físico for fornecido, subir para a API Files do Gemini
            if file_path:
                logger.info("Enviando arquivo temporário para API do Gemini: %s (%s)", file_path, mime_type)
                uploaded_file = genai.upload_file(path=file_path, mime_type=mime_type)
                contents.append(uploaded_file)

            if isbn_data:
                contents.append(f"\n[DADOS DE REFERÊNCIA OBTIDOS PELO ISBN NA WEB]:\n{json.dumps(isbn_data, ensure_ascii=False)}")

            if text_content:
                contents.append(f"\nDados ou texto adicional do usuário:\n{text_content}")

            logger.info("Chamando API do Gemini (gemini-2.5-flash) com structured JSON...")
            response = self.model.generate_content(
                contents,
                generation_config={"response_mime_type": "application/json"}
            )

            response_text = response.text.strip()
            logger.info("Resposta recebida da API do Gemini.")

            # Limpar qualquer markdown restante
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()
            if response_text.startswith("```"):
                response_text = response_text.replace("```", "", 1)

            extracted_data = json.loads(response_text.strip())

            # 1. Mapear capa e avaliações vindas do pré-processamento
            if isbn_data:
                if 'temp_cover_image' in isbn_data and isbn_data['temp_cover_image']:
                    extracted_data['temp_cover_image'] = isbn_data['temp_cover_image']
                
                # Integrar avaliações se obtidas da API e não preenchidas
                if isbn_data.get('average_rating') is not None and extracted_data.get('average_rating') is None:
                    extracted_data['average_rating'] = isbn_data.get('average_rating')
                if isbn_data.get('ratings_count') is not None and extracted_data.get('ratings_count') is None:
                    extracted_data['ratings_count'] = isbn_data.get('ratings_count')

            # 2. Gerar link de parceiro da Amazon deterministicamente
            isbn_val = extracted_data.get('isbn') or (isbn_data.get('isbn') if isbn_data else None)
            if isbn_val:
                isbn10 = self._get_isbn_10(isbn_val)
                if isbn10:
                    extracted_data['purchase_partner_name'] = 'Amazon'
                    extracted_data['purchase_partner_url'] = f"https://www.amazon.com.br/dp/{isbn10}"
            else:
                extracted_data['purchase_partner_name'] = 'Amazon'
                extracted_data['purchase_partner_url'] = ""

            # Garantir casting e valores default válidos
            try:
                extracted_data['average_rating'] = float(extracted_data.get('average_rating', 0.0) or 0.0)
            except (ValueError, TypeError):
                extracted_data['average_rating'] = 0.0

            try:
                extracted_data['ratings_count'] = int(extracted_data.get('ratings_count', 0) or 0)
            except (ValueError, TypeError):
                extracted_data['ratings_count'] = 0

            # Mapear Autor e Categoria no banco de dados local
            author_name = extracted_data.get('author_name', '').strip()
            category_name = extracted_data.get('category_name', '').strip()

            author_id = None
            category_id = None

            if author_name:
                # Busca case-insensitive
                author_obj = Author.objects.filter(name__iexact=author_name).first()
                if author_obj:
                    author_id = author_obj.id
                    extracted_data['author_name'] = author_obj.name  # Normalizar nome exato
                else:
                    logger.info("Autor não encontrado no banco local: '%s'", author_name)

            if category_name:
                category_obj = Category.objects.filter(name__iexact=category_name).first()
                if category_obj:
                    category_id = category_obj.id
                    extracted_data['category_name'] = category_obj.name  # Normalizar nome exato
                else:
                    logger.info("Categoria não encontrada no banco local: '%s'", category_name)

            extracted_data['author_id'] = author_id
            extracted_data['category_id'] = category_id

            return extracted_data

        except json.JSONDecodeError as e:
            logger.error("Erro ao decodificar JSON retornado pelo Gemini: %s. Resposta: %s", e, response_text)
            raise ValueError("A IA não retornou um formato JSON válido.") from e
        except Exception as e:
            logger.error("Erro geral no AIBookAssistantService: %s", e, exc_info=True)
            raise e
        finally:
            # Excluir o arquivo da nuvem da API do Gemini para limpeza
            if uploaded_file:
                try:
                    logger.info("Limpando arquivo da API do Gemini: %s", uploaded_file.name)
                    uploaded_file.delete()
                except Exception as e:
                    logger.warning("Falha ao remover arquivo temporário do Gemini: %s", e)

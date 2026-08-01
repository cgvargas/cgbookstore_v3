"""
Serviço agregador unificado de metadados de livros.
Combina dados da Amazon Brasil, Google Books API, Open Library e Project Gutenberg.
"""

import logging
from typing import Dict, Any, Optional
from core.models import Book, Author, Category
from core.utils.google_books_api import get_book_by_isbn as get_google_book_by_isbn, search_books as search_google_books
from partners.services.amazon_api_service import AmazonAPIService, AmazonProductData
from partners.services.amazon_service import AmazonURLNormalizer

logger = logging.getLogger(__name__)


class BookMetadataAggregator:
    """
    Agrega metadados de múltiplas fontes externas de forma não-destrutiva.
    Prioriza a Amazon Brasil para links comerciais, preços em R$, ASIN e formatos (Kindle/Físico),
    e o Google Books para descrições, notas médias e biografias.
    """

    @classmethod
    def fetch_and_enrich_book(cls, book: Book, force: bool = False) -> Dict[str, Any]:
        """
        Busca metadados nas fontes externas para um livro cadastrado e aplica as melhorias.
        Returns a dict com o resumo das alterações realizadas.
        """
        changes = []
        amazon_data: Optional[AmazonProductData] = None
        google_data: Optional[Dict[str, Any]] = None

        # 1. Tentar consultar na Amazon Brasil por ASIN, ISBN ou URL existente
        if book.purchase_partner_url and AmazonURLNormalizer.is_amazon_url(book.purchase_partner_url):
            amazon_data = AmazonAPIService.fetch_by_url(book.purchase_partner_url)

        if not amazon_data and book.isbn:
            amazon_data = AmazonAPIService.search_by_isbn(book.isbn)

        if not amazon_data and book.title:
            query = f"{book.title} {book.author.name if book.author else ''}".strip()
            results = AmazonAPIService.search_by_keywords(query, max_results=1)
            if results:
                amazon_data = results[0]

        # 2. Consultar Google Books se ISBN ou Título estiverem disponíveis
        if book.isbn:
            google_data = get_google_book_by_isbn(book.isbn)

        if not google_data and book.title:
            g_results = search_google_books(title=book.title, author=book.author.name if book.author else None, max_results=1)
            if g_results and g_results.get('books'):
                google_data = g_results['books'][0]

        # 3. Aplicar dados da Amazon Brasil se encontrados
        if amazon_data:
            if not book.purchase_partner_name or force:
                book.purchase_partner_name = "Amazon"
                changes.append("Parceiro definido como Amazon")

            if not book.purchase_partner_url or force:
                book.purchase_partner_url = amazon_data.affiliate_url
                changes.append("URL de Afiliado da Amazon atualizada")
            elif AmazonURLNormalizer.is_amazon_url(book.purchase_partner_url):
                # Normalizar URL existente com tag cgbookstore-20
                normalized = AmazonURLNormalizer.normalize(book.purchase_partner_url)
                if book.purchase_partner_url != normalized:
                    book.purchase_partner_url = normalized
                    changes.append("URL da Amazon normalizada com tag de afiliado")

            if (not book.price or force) and amazon_data.price:
                book.price = amazon_data.price
                changes.append(f"Preço atualizado para R$ {amazon_data.price:.2f}")

            if amazon_data.available_kindle and not book.available_kindle:
                book.available_kindle = True
                changes.append("Formato Kindle marcado como disponível")

            if amazon_data.available_print and not book.available_print:
                book.available_print = True
                changes.append("Formato Impresso marcado como disponível")

        # 4. Aplicar dados do Google Books se encontrados
        if google_data:
            if not book.google_books_id and google_data.get('google_book_id'):
                book.google_books_id = google_data['google_book_id']
                changes.append("ID do Google Books associado")

            if (not book.description or force) and google_data.get('description'):
                book.description = google_data['description']
                changes.append("Descrição atualizada via Google Books")

            if (not book.page_count or force) and google_data.get('page_count'):
                book.page_count = google_data['page_count']
                changes.append(f"Número de páginas definido para {google_data['page_count']}")

            if (not book.average_rating or force) and google_data.get('average_rating'):
                book.average_rating = google_data['average_rating']
                book.ratings_count = google_data.get('ratings_count', 0)
                changes.append(f"Avaliação média atualizada para {google_data['average_rating']}")

            if (not book.preview_link or force) and google_data.get('preview_link'):
                book.preview_link = google_data['preview_link']

            if (not book.info_link or force) and google_data.get('info_link'):
                book.info_link = google_data['info_link']

        if changes:
            book.save()
            logger.info(f"[METADATA AGGREGATOR] Livro '{book.title}' enriquecido com {len(changes)} alterações.")

        return {
            'success': True,
            'book': book,
            'changes': changes,
            'has_amazon': bool(amazon_data),
            'has_google': bool(google_data),
            'amazon_source': amazon_data.source if amazon_data else None
        }

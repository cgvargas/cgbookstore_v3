"""
Sistema de Retrieval-Augmented Generation (RAG) para o Chatbot Literário.

Este módulo implementa busca de conhecimento verificado no banco de dados
para reduzir alucinações da IA e garantir respostas factuais.

Pilares do RAG:
1. Base de Conhecimento Estruturada: Busca no banco de dados real
2. Mecanismo de Busca Refinado: Contexto persistente + busca inteligente
3. Validação de Respostas: Dados verificados injetados no prompt
"""

import logging
from typing import Dict, List, Optional, Any
from django.db.models import Q
from core.models import Book, Author, Category

logger = logging.getLogger(__name__)


class KnowledgeRetrieval:
    """
    Serviço de busca de conhecimento verificado para RAG.

    Responsável por:
    - Buscar livros no banco de dados
    - Extrair séries de livros (quando aplicável)
    - Formatar dados para injeção no prompt da IA
    - Manter contexto de referências na conversa
    """

    def __init__(self):
        """Inicializa o serviço de Knowledge Retrieval."""
        self.conversation_context = {}  # Armazena contexto da conversa (ex: livro mencionado)

    def search_books_by_title(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca livros por título (busca parcial, case-insensitive).

        Args:
            title: Título ou parte do título a buscar
            limit: Número máximo de resultados

        Returns:
            Lista de dicionários com dados estruturados dos livros
        """
        try:
            books = Book.objects.filter(
                Q(title__icontains=title) | Q(subtitle__icontains=title)
            ).select_related('author', 'category')[:limit]

            return [self._serialize_book(book) for book in books]
        except Exception as e:
            logger.error(f"Erro ao buscar livros por título '{title}': {e}", exc_info=True)
            return []

    def search_books_by_author(self, author_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca livros por nome do autor.

        Args:
            author_name: Nome ou parte do nome do autor
            limit: Número máximo de resultados

        Returns:
            Lista de dicionários com dados estruturados dos livros
        """
        try:
            books = Book.objects.filter(
                author__name__icontains=author_name
            ).select_related('author', 'category')[:limit]

            return [self._serialize_book(book) for book in books]
        except Exception as e:
            logger.error(f"Erro ao buscar livros do autor '{author_name}': {e}", exc_info=True)
            return []

    def search_books_by_category(self, category_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca livros por categoria/gênero.

        Args:
            category_name: Nome da categoria (ex: "Ficção Científica", "Romance")
            limit: Número máximo de resultados

        Returns:
            Lista de dicionários com dados estruturados dos livros
        """
        try:
            books = Book.objects.filter(
                category__name__icontains=category_name
            ).select_related('author', 'category')[:limit]

            return [self._serialize_book(book) for book in books]
        except Exception as e:
            logger.error(f"Erro ao buscar livros da categoria '{category_name}': {e}", exc_info=True)
            return []

    def get_book_by_exact_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Busca livro por título exato (match exato).

        Args:
            title: Título exato do livro

        Returns:
            Dicionário com dados do livro ou None se não encontrado
        """
        try:
            book = Book.objects.select_related('author', 'category').get(
                title__iexact=title
            )
            return self._serialize_book(book)
        except Book.DoesNotExist:
            logger.warning(f"Livro com título exato '{title}' não encontrado")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar livro exato '{title}': {e}", exc_info=True)
            return None

    def get_author_info(self, author_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações sobre um autor.

        Args:
            author_name: Nome do autor

        Returns:
            Dicionário com dados do autor ou None se não encontrado
        """
        try:
            author = Author.objects.get(name__iexact=author_name)
            return {
                'name': author.name,
                'bio': author.bio or "Biografia não disponível",
                'books_count': author.books.count(),
                'website': author.website,
                'twitter': author.twitter,
                'instagram': author.instagram,
            }
        except Author.DoesNotExist:
            logger.warning(f"Autor '{author_name}' não encontrado")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar autor '{author_name}': {e}", exc_info=True)
            return None

    def get_books_by_series_detection(self, title: str) -> List[Dict[str, Any]]:
        """
        Tenta detectar série baseado em padrões comuns no título.

        Exemplos:
        - "Crônicas de Nárnia" -> busca todos os livros com "Nárnia"
        - "Harry Potter" -> busca todos os livros com "Harry Potter"

        Args:
            title: Título para detectar série

        Returns:
            Lista de livros da série (se detectado)
        """
        try:
            # Padrões comuns de séries
            series_keywords = [
                'Crônicas', 'Harry Potter', 'Senhor dos Anéis', 'Hobbit',
                'Fundação', 'Dune', 'Game of Thrones', 'Gelo e Fogo',
                'Percy Jackson', 'Divergente', 'Hunger Games', 'Jogos Vorazes'
            ]

            # Detecta se o título contém algum indicador de série
            for keyword in series_keywords:
                if keyword.lower() in title.lower():
                    return self.search_books_by_title(keyword, limit=20)

            return []
        except Exception as e:
            logger.error(f"Erro ao detectar série para '{title}': {e}", exc_info=True)
            return []

    def store_conversation_reference(self, reference_id: str, book_data: Dict[str, Any]):
        """
        Armazena referência de livro mencionado na conversa para uso posterior.

        Args:
            reference_id: Identificador da referência (ex: "livro_1", "livro_2")
            book_data: Dados do livro a armazenar
        """
        self.conversation_context[reference_id] = book_data

    def get_conversation_reference(self, reference_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera referência de livro mencionado anteriormente na conversa.

        Args:
            reference_id: Identificador da referência (ex: "livro_1", "livro_3")

        Returns:
            Dados do livro ou None se não encontrado
        """
        return self.conversation_context.get(reference_id)

    def clear_conversation_context(self):
        """Limpa o contexto da conversa (quando usuário inicia nova conversa)."""
        self.conversation_context.clear()

    def format_book_for_prompt(self, book_data: Dict[str, Any]) -> str:
        """
        Formata dados de um livro para injeção no prompt da IA.

        Args:
            book_data: Dados estruturados do livro

        Returns:
            String formatada para o prompt
        """
        author_name = book_data.get('author_name', 'Autor desconhecido')
        category_name = book_data.get('category_name', 'Categoria não especificada')

        prompt_text = f"""[DADOS VERIFICADOS]
Título: {book_data['title']}
Autor: {author_name}
Categoria/Gênero: {category_name}
"""

        if book_data.get('subtitle'):
            prompt_text += f"Subtítulo: {book_data['subtitle']}\n"

        if book_data.get('description'):
            # Limita descrição a 300 caracteres para não poluir o prompt
            desc = book_data['description'][:300]
            if len(book_data['description']) > 300:
                desc += "..."
            prompt_text += f"Descrição: {desc}\n"

        if book_data.get('publisher'):
            prompt_text += f"Editora: {book_data['publisher']}\n"

        if book_data.get('publication_year'):
            prompt_text += f"Ano de Publicação: {book_data['publication_year']}\n"

        if book_data.get('page_count'):
            prompt_text += f"Páginas: {book_data['page_count']}\n"

        if book_data.get('average_rating'):
            prompt_text += f"Avaliação Média: {book_data['average_rating']}/5.0\n"

        prompt_text += "[/DADOS VERIFICADOS]\n\n"
        prompt_text += "IMPORTANTE: Responda usando APENAS estes dados verificados. NÃO invente informações."

        return prompt_text

    def format_multiple_books_for_prompt(self, books_data: List[Dict[str, Any]], max_books: int = 5) -> str:
        """
        Formata múltiplos livros para injeção no prompt da IA.

        Args:
            books_data: Lista de dados estruturados de livros
            max_books: Número máximo de livros a incluir no prompt

        Returns:
            String formatada para o prompt
        """
        if not books_data:
            return "[NENHUM DADO VERIFICADO DISPONÍVEL]\n\nRESPOSTA: Desculpe, não encontrei informações verificadas sobre esse assunto em nossa base de dados."

        books_to_include = books_data[:max_books]

        prompt_text = f"[DADOS VERIFICADOS - {len(books_to_include)} LIVROS ENCONTRADOS]\n\n"

        for idx, book in enumerate(books_to_include, 1):
            author_name = book.get('author_name', 'Autor desconhecido')
            category_name = book.get('category_name', 'Categoria não especificada')

            prompt_text += f"{idx}. **{book['title']}** ({author_name})\n"
            prompt_text += f"   Gênero: {category_name}\n"

            if book.get('description'):
                desc = book['description'][:150]
                if len(book['description']) > 150:
                    desc += "..."
                prompt_text += f"   Sinopse: {desc}\n"

            prompt_text += "\n"

        prompt_text += "[/DADOS VERIFICADOS]\n\n"
        prompt_text += "IMPORTANTE: Recomende APENAS estes livros listados acima. NÃO invente outros títulos."

        return prompt_text

    def _serialize_book(self, book: Book) -> Dict[str, Any]:
        """
        Serializa um objeto Book do Django para dicionário.

        Args:
            book: Instância do modelo Book

        Returns:
            Dicionário com dados estruturados
        """
        return {
            'id': book.id,
            'title': book.title,
            'subtitle': book.subtitle,
            'author_name': book.author.name if book.author else None,
            'author_id': book.author.id if book.author else None,
            'category_name': book.category.name if book.category else None,
            'category_id': book.category.id if book.category else None,
            'description': book.description,
            'publisher': book.publisher,
            'publication_year': book.publication_date.year if book.publication_date else None,
            'isbn': book.isbn,
            'page_count': book.page_count,
            'average_rating': float(book.average_rating) if book.average_rating else None,
            'ratings_count': book.ratings_count,
            'language': book.language,
            'cover_image_url': book.cover_image.url if book.cover_image else None,
            'purchase_partner': book.purchase_partner_name,
            'purchase_url': book.purchase_partner_url,
        }

    def search_news_articles(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Busca artigos de notícias relevantes no sistema de News.

        Args:
            query: Termo de busca
            limit: Número máximo de resultados

        Returns:
            Lista de dicionários com dados dos artigos
        """
        try:
            from news.models import Article
            from django.db.models import Q

            # Buscar artigos publicados que contenham o termo
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                is_published=True
            ).order_by('-published_at')[:limit]

            return [self._serialize_article(article) for article in articles]
        except Exception as e:
            logger.error(f"Erro ao buscar artigos de notícias para '{query}': {e}", exc_info=True)
            return []

    def _serialize_article(self, article) -> Dict[str, Any]:
        """Serializa um artigo de notícias para dicionário."""
        return {
            'id': article.id,
            'title': article.title,
            'excerpt': article.excerpt if article.excerpt else '',
            'content_type': article.get_content_type_display() if hasattr(article, 'get_content_type_display') else 'Artigo',
            'published_at': article.published_at.strftime('%d/%m/%Y') if article.published_at else None,
            'url': article.get_absolute_url() if hasattr(article, 'get_absolute_url') else None,
        }

    def format_news_for_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """
        Formata artigos de notícias para injeção no prompt da IA.

        Args:
            articles: Lista de dados de artigos

        Returns:
            String formatada para o prompt
        """
        if not articles:
            return ""

        prompt_text = f"[NOTÍCIAS ENCONTRADAS - {len(articles)} ARTIGOS]\n\n"

        for idx, article in enumerate(articles, 1):
            prompt_text += f"{idx}. **{article['title']}**\n"
            if article.get('excerpt'):
                excerpt = article['excerpt'][:200]
                if len(article['excerpt']) > 200:
                    excerpt += "..."
                prompt_text += f"   {excerpt}\n"
            if article.get('published_at'):
                prompt_text += f"   Publicado: {article['published_at']}\n"
            prompt_text += "\n"

        prompt_text += "[/NOTÍCIAS ENCONTRADAS]\n\n"
        prompt_text += "IMPORTANTE: Use estas informações APENAS como referência. Mencione que são notícias do nosso blog."

        return prompt_text


# Singleton global para reutilizar instância
_knowledge_retrieval_service = None


def get_knowledge_retrieval_service() -> KnowledgeRetrieval:
    """Retorna instância singleton do serviço de Knowledge Retrieval."""
    global _knowledge_retrieval_service
    if _knowledge_retrieval_service is None:
        _knowledge_retrieval_service = KnowledgeRetrieval()
    return _knowledge_retrieval_service

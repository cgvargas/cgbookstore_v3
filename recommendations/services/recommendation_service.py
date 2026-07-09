import logging
from django.db.models import Count, Q
from core.models import Book
from accounts.models import BookShelf
from core.utils.google_books_api import search_books

logger = logging.getLogger(__name__)


class BookRecommendationService:
    """
    Serviço responsável por gerar recomendações inteligentes para a página de detalhes do livro.
    Utiliza relacionamentos locais de autor/categoria, filtragem colaborativa básica com base
    nas prateleiras dos usuários, e faz fallback inteligente para a API do Google Books.
    """

    @staticmethod
    def get_recommendations_for_book(book, limit=4) -> dict:
        """
        Retorna um dicionário com diferentes listas de recomendações para abas no template.
        """
        author_recs = BookRecommendationService.get_author_recommendations(book, limit)
        category_recs = BookRecommendationService.get_category_recommendations(book, limit)
        collab_recs = BookRecommendationService.get_collaborative_recommendations(book, limit)
        
        # Se temos poucas recomendações locais de categoria, enriquecemos com Google Books
        if len(category_recs) < limit:
            needed = limit - len(category_recs)
            google_recs = BookRecommendationService.get_google_books_recommendations(book, needed)
            
            # Mescla sem duplicados
            seen_titles = {b.title.lower() for b in category_recs}
            seen_titles.add(book.title.lower())
            
            merged_category = list(category_recs)
            for b in google_recs:
                if b.title.lower() not in seen_titles:
                    merged_category.append(b)
                    seen_titles.add(b.title.lower())
            category_recs = merged_category

        return {
            'same_author': author_recs,
            'same_category': category_recs[:limit],
            'collaborative': collab_recs,
        }

    @staticmethod
    def get_author_recommendations(book, limit=4):
        """Retorna outros livros do mesmo autor no banco local."""
        if not book.author:
            return Book.objects.none()
        return Book.objects.filter(
            author=book.author
        ).exclude(
            id=book.id
        ).filter(
            cover_image__isnull=False
        ).exclude(
            cover_image=''
        ).select_related('author')[:limit]

    @staticmethod
    def get_category_recommendations(book, limit=4):
        """Retorna outros livros da mesma categoria no banco local."""
        if not book.category:
            return Book.objects.none()
        return Book.objects.filter(
            category=book.category
        ).exclude(
            id=book.id
        ).filter(
            cover_image__isnull=False
        ).exclude(
            cover_image=''
        ).select_related('author', 'category')[:limit]

    @staticmethod
    def get_collaborative_recommendations(book, limit=4):
        """
        Retorna livros frequentemente adicionados por leitores que também têm
        o livro atual na biblioteca (associação de prateleiras).
        """
        # IDs de usuários que têm este livro em qualquer prateleira
        user_ids = list(BookShelf.objects.filter(book=book).values_list('user_id', flat=True))
        if not user_ids:
            return Book.objects.none()

        # Livros mais comuns nas prateleiras desses usuários
        associated_books = (
            Book.objects.filter(
                in_shelves__user_id__in=user_ids
            )
            .exclude(id=book.id)
            .filter(cover_image__isnull=False)
            .exclude(cover_image='')
            .annotate(occurrences=Count('in_shelves'))
            .select_related('author')
            .order_by('-occurrences')[:limit]
        )
        return associated_books

    @staticmethod
    def get_google_books_recommendations(book, limit=4):
        """
        Busca livros por assunto na Google Books API e retorna como objetos locais
        (se já cadastrados) ou como objetos na memória temporária para exibição.
        """
        if not book.category and not book.title:
            return []

        # Se o livro tem categoria, busca por ela. Caso contrário, pelo título
        query = f"subject:{book.category.name}" if book.category else book.title
        try:
            results = search_books(query=query, max_results=limit * 2)
            items = results.get('items', [])
            
            recs = []
            seen_titles = {book.title.lower()}
            
            for item in items:
                vol_info = item.get('volumeInfo', {})
                title = vol_info.get('title', '')
                if not title or title.lower() in seen_titles:
                    continue
                
                google_id = item.get('id', '')
                
                # Verifica se o livro já existe no banco local por ID ou Título
                local_book = Book.objects.filter(
                    Q(google_books_id=google_id) | Q(title__iexact=title)
                ).select_related('author').first()
                
                if local_book:
                    recs.append(local_book)
                    seen_titles.add(title.lower())
                else:
                    # Cria um objeto Book temporário em memória (não salvo no DB)
                    authors = vol_info.get('authors', [])
                    author_name = authors[0] if authors else "Vários Autores"
                    
                    from core.models import Author
                    author_obj = Author.objects.filter(name__iexact=author_name).first()
                    if not author_obj:
                        author_obj = Author(name=author_name)
                    
                    image_links = vol_info.get('imageLinks', {})
                    cover_url = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ''
                    
                    temp_book = Book(
                        title=title,
                        author=author_obj,
                        category=book.category,
                        description=vol_info.get('description', ''),
                        google_books_id=google_id
                    )
                    
                    # Injeta a URL externa temporária
                    if cover_url:
                        temp_book.cover_url_temp = cover_url
                        
                    recs.append(temp_book)
                    seen_titles.add(title.lower())
                
                if len(recs) >= limit:
                    break
                    
            return recs
            
        except Exception as e:
            logger.error(f"Erro ao buscar recomendações do Google Books para {book.title}: {str(e)}")
            return []

    @staticmethod
    def get_ai_personalized_recommendations(user, limit=6) -> dict:
        """
        Retorna recomendações preditivas personalizadas de livros, autores, notícias,
        eventos e adaptações baseando-se no AIReaderProfile do usuário.
        """
        from django.utils import timezone
        from recommendations.services.reader_profile_service import ReaderProfileService
        from news.models import Article
        from core.models import Event, Author, Video
        
        # 1. Recuperar ou inicializar o perfil do leitor
        profile = ReaderProfileService.get_or_create_profile(user)
        
        # Se as afinidades não estão calculadas, atualiza-as
        if not profile.categories_interest and not profile.authors_interest:
            ReaderProfileService.update_profile_weights(user)
            profile.refresh_from_db()
            
        categories = list(profile.categories_interest.keys())
        authors = list(profile.authors_interest.keys())

        # FALLBACKS caso o perfil esteja vazio
        if not categories:
            categories = ['Ficção', 'Fantasia', 'Romance', 'Distopia', 'Suspense']
        if not authors:
            authors = ['J.R.R. Tolkien', 'George Orwell', 'Stephen King']

        # 2. Recomendar LIVROS
        books_qs = Book.objects.filter(
            Q(category__name__in=categories) | Q(author__name__in=authors)
        ).filter(
            cover_image__isnull=False
        ).exclude(
            cover_image=''
        ).select_related('author', 'category').distinct()
        
        def book_score(b):
            score = 0.0
            if b.category and b.category.name in profile.categories_interest:
                score += profile.categories_interest[b.category.name]
            if b.author and b.author.name in profile.authors_interest:
                score += profile.authors_interest[b.author.name] * 1.5
            return score
            
        recommended_books = sorted(books_qs, key=book_score, reverse=True)[:limit]
        
        if len(recommended_books) < limit:
            needed = limit - len(recommended_books)
            additional_books = Book.objects.filter(
                cover_image__isnull=False
            ).exclude(
                cover_image=''
            ).exclude(
                id__in=[b.id for b in recommended_books]
            ).select_related('author', 'category')[:needed]
            recommended_books.extend(additional_books)

        # 3. Recomendar AUTORES
        recommended_authors = Author.objects.filter(
            name__in=authors
        ).distinct()[:limit]
        if len(recommended_authors) < limit:
            needed = limit - len(recommended_authors)
            additional_authors = Author.objects.exclude(
                id__in=[a.id for a in recommended_authors]
            )[:needed]
            recommended_authors = list(recommended_authors) + list(additional_authors)

        # 4. Recomendar NOTÍCIAS (Article)
        articles_qs = Article.objects.filter(
            Q(category__name__in=categories) | Q(tags__name__in=categories)
        ).filter(is_published=True).distinct().order_by('-published_at')
        recommended_news = list(articles_qs[:limit])
        if len(recommended_news) < limit:
            needed = limit - len(recommended_news)
            additional_news = Article.objects.filter(
                is_published=True
            ).exclude(
                id__in=[n.id for n in recommended_news]
            ).order_by('-published_at')[:needed]
            recommended_news = recommended_news + list(additional_news)

        # 5. Recomendar EVENTOS (Event)
        # Event usa status e start_date — filtra próximos eventos com status 'upcoming'
        events_qs = Event.objects.filter(
            start_date__gt=timezone.now(),
            status='upcoming'
        ).filter(
            Q(title__icontains=categories[0]) if categories else Q()
        ).distinct().order_by('start_date')
        recommended_events = list(events_qs[:limit])
        if not recommended_events:
            recommended_events = list(Event.objects.filter(
                start_date__gt=timezone.now(),
                status='upcoming'
            ).order_by('start_date')[:limit])

        # 6. Recomendar ADAPTAÇÕES (Video com tipo 'adaptation')
        adaptations_qs = Video.objects.filter(
            video_type='adaptation'
        ).filter(
            Q(related_book__category__name__in=categories) | Q(related_author__name__in=authors)
        ).distinct().order_by('-views_count')
        recommended_adaptations = adaptations_qs[:limit]
        if len(recommended_adaptations) < limit:
            needed = limit - len(recommended_adaptations)
            additional_adaptations = Video.objects.filter(
                video_type='adaptation'
            ).exclude(
                id__in=[v.id for v in recommended_adaptations]
            ).order_by('-views_count')[:needed]
            recommended_adaptations = list(recommended_adaptations) + list(additional_adaptations)

        return {
            'books': recommended_books,
            'authors': recommended_authors,
            'news': recommended_news,
            'events': recommended_events,
            'adaptations': recommended_adaptations
        }


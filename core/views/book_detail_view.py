"""
View de Detalhes do Livro.
Exibe informações completas de um livro específico.
"""
from django.views.generic import DetailView
from core.models import Book


class BookDetailView(DetailView):
    """
    View para exibir detalhes completos de um livro.

    Acessível via slug em: /livros/<slug>/
    Suporta dados locais e integrados do Google Books API.
    """
    model = Book
    template_name = 'core/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        """Adiciona contexto extra para o template."""
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        # 1. Histórico de visitas do usuário na sessão
        visited_books = self.request.session.get('visited_books', [])
        context['visited_before'] = book.id in visited_books
        if book.id not in visited_books:
            visited_books.append(book.id)
            self.request.session['visited_books'] = visited_books
            self.request.session.modified = True

        # 2. Contexto de biblioteca e cliques anteriores de compra
        context['in_library'] = False
        context['shelf_status'] = None
        context['has_purchased_before'] = False

        if self.request.user.is_authenticated:
            from accounts.models import BookShelf
            shelves = list(BookShelf.objects.filter(user=self.request.user, book=book).values_list('shelf_type', flat=True))
            context['in_library'] = len(shelves) > 0
            if 'favorites' in shelves:
                context['shelf_status'] = 'favorites'
            elif 'reading' in shelves:
                context['shelf_status'] = 'reading'
            elif 'read' in shelves:
                context['shelf_status'] = 'read'
            elif 'to_read' in shelves:
                context['shelf_status'] = 'to_read'
            elif 'abandoned' in shelves:
                context['shelf_status'] = 'abandoned'
            elif 'custom' in shelves:
                context['shelf_status'] = 'custom'

            from partners.models import AffiliatePartnerClick
            context['has_purchased_before'] = AffiliatePartnerClick.objects.filter(
                user=self.request.user, book=book
            ).exists()
        else:
            session_key = self.request.session.session_key
            if session_key:
                from partners.models import AffiliatePartnerClick
                context['has_purchased_before'] = AffiliatePartnerClick.objects.filter(
                    session_key=session_key, book=book
                ).exists()

        # 3. Recomendações e IA ("Vale a pena ler?")
        from recommendations.services import BookRecommendationService
        from core.services.ai_review_service import AIReviewService
        from django.core.cache import cache

        context['recommendations'] = BookRecommendationService.get_recommendations_for_book(book, limit=4)
        
        # 1. Carrega a resenha de IA (busca primeiro no banco de dados, depois na IA)
        ai_review = book.ai_review
        if not ai_review:
            ai_cache_key = f"ai_review:{book.id}"
            ai_review = cache.get(ai_cache_key)
            if not ai_review:
                ai_review = AIReviewService.generate_review(book)
                if ai_review:
                    book.ai_review = ai_review
                    book.save(update_fields=['ai_review', 'updated_at'])
                    cache.set(ai_cache_key, ai_review, 86400 * 30)  # 30 dias
        context['ai_review'] = ai_review

        # 2. Carrega a análise expandida de IA (busca primeiro no banco de dados, depois na IA)
        ai_expanded_review = book.ai_expanded_analysis
        if not ai_expanded_review:
            ai_expanded_cache_key = f"ai_expanded_review:{book.id}"
            ai_expanded_review = cache.get(ai_expanded_cache_key)
            if not ai_expanded_review:
                ai_expanded_review = AIReviewService.generate_expanded_analysis(book)
                if ai_expanded_review:
                    book.ai_expanded_analysis = ai_expanded_review
                    book.save(update_fields=['ai_expanded_analysis', 'updated_at'])
                    cache.set(ai_expanded_cache_key, ai_expanded_review, 86400 * 30)
        context['ai_expanded_review'] = ai_expanded_review


        # 4. Gamificação: Atribui 5 XP por clicar em recomendação inteligente
        ref = self.request.GET.get('ref')
        if ref == 'recommendation' and self.request.user.is_authenticated:
            xp_cache_key = f"xp_rec:{self.request.user.id}:{book.id}"
            if not cache.get(xp_cache_key):
                self.request.user.profile.add_xp(5)
                cache.set(xp_cache_key, True, 86400)  # 24 horas

        # Livros relacionados da mesma categoria (lógica existente mantida como fallback)
        context['related_books'] = Book.objects.filter(
            category=book.category
        ).exclude(id=book.id)[:4]


        # Vídeos relacionados ao livro (adaptações, trailers, entrevistas)
        from core.models import Video
        context['book_videos'] = Video.objects.filter(
            related_book=book,
            active=True
        ).order_by('-featured', '-created_at')

        # Artigos/notícias relacionados ao livro (adaptações, resenhas, eventos)
        from news.models import Article
        context['book_articles'] = Article.objects.filter(
            related_book=book,
            is_published=True
        ).select_related('category').order_by('-published_at')[:3]

        # === ESTATÍSTICAS DE AVALIAÇÃO (Visíveis para todos) ===
        from accounts.models import BookReview
        from django.db.models import Count, Avg

        # Coletar estatísticas de TODAS as resenhas do livro
        # (inclui publicas e privadas para formar a nota real do livro)
        all_reviews = BookReview.objects.filter(book=book)
        total_reviews = all_reviews.count()
        
        # Dicionários padrão
        star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        star_percentages = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        avg_rating = 0.0

        if total_reviews > 0:
            # Calcula a média exata (Decimal)
            avg_result = all_reviews.aggregate(Avg('rating'))
            avg_rating = round(avg_result['rating__avg'] or 0, 1)

            # Agrupa e conta por nota
            for review in all_reviews:
                # Arredondando para a estrela mais próxima (ex: 4.5 vira 5, 4.4 vira 4)
                # Para estatística visual simplificada.
                star = int(round(review.rating))
                # Limita entre 1 e 5
                star = max(1, min(5, star))
                star_counts[star] += 1

            # Calcula os percentuais
            for star in range(1, 6):
                star_percentages[star] = int((star_counts[star] / total_reviews) * 100)

        context['review_stats'] = {
            'total': total_reviews,
            'average': avg_rating,
            'counts': star_counts,
            'percentages': star_percentages
        }

        # Inicializa o contexto base do usuário
        context['user_is_reading'] = False
        context['reading_progress'] = None
        context['custom_shelves'] = []

        if self.request.user.is_authenticated:
            # Buscar prateleiras personalizadas (lógica existente mantida)
            profile = self.request.user.profile
            context['custom_shelves'] = profile.get_custom_shelves()

            # Importa os modelos necessários
            from accounts.models import ReadingProgress, BookShelf
            from accounts.forms import BookReviewForm

            # Adicionando Resenhas ao Contexto (limitado à última enviada, e com métricas)
            context['reviews'] = BookReview.objects.filter(
                book=book, 
                is_public=True
            ).select_related('user', 'user__profile').exclude(user=self.request.user).annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            ).order_by('-created_at')[:1]
            
            # Buscar a resenha do próprio usuário
            user_review = BookReview.objects.filter(book=book, user=self.request.user).annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            ).first()
            context['user_review'] = user_review
            context['review_form'] = BookReviewForm(instance=user_review)

            # Verifica de forma explícita se o livro está na prateleira "Lendo"
            is_reading = BookShelf.objects.filter(
                user=self.request.user,
                book=book,
                shelf_type='reading'
            ).exists()
            context['user_is_reading'] = is_reading

            # Se estiver lendo, busca e adiciona o objeto de progresso
            if is_reading:
                progress = ReadingProgress.objects.filter(
                    user=self.request.user,
                    book=book,
                ).first()  # Simplificado para pegar o progresso existente
                context['reading_progress'] = progress
        else:
            # Visitante não logado vê apenas a última resenha pública
            context['reviews'] = BookReview.objects.filter(
                book=book, 
                is_public=True
            ).select_related('user', 'user__profile').annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            ).order_by('-created_at')[:1]

        return context

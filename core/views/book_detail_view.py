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

        # Livros relacionados da mesma categoria (lógica existente mantida)
        context['related_books'] = Book.objects.filter(
            category=book.category
        ).exclude(id=book.id)[:4]

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

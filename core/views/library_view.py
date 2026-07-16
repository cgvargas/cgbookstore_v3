"""
View para a Biblioteca pessoal do usuário.
Integrada com os models de BookShelf, ReadingProgress, etc.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Prefetch
from django.core.cache import cache
from accounts.models import BookShelf, ReadingProgress, BookReview


class LibraryView(LoginRequiredMixin, TemplateView):
    """
    View para a Biblioteca pessoal do usuário.
    Exibe prateleiras, progresso de leitura e estatísticas.
    """
    template_name = 'core/library.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    @staticmethod
    def _serialize_recommended_article(article):
        """Serializa uma notícia recomendada usando o campo real do model Article."""
        featured_image = article.featured_image
        return {
            'id': article.id,
            'title': article.title,
            'subtitle': article.subtitle,
            'image': {'url': featured_image.url} if featured_image else None,
            'published_at': (
                article.published_at.strftime('%d/%m/%Y')
                if hasattr(article.published_at, 'strftime')
                else str(article.published_at)
            ),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Perfil do usuário
        profile = getattr(user, 'profile', None)
        context['profile'] = profile

        # Tema visual selecionado pelo usuário
        context['selected_theme'] = profile.theme_preference if profile else 'fantasy'

        # Contadores de prateleiras
        context['favorites_count'] = BookShelf.objects.filter(
            user=user, shelf_type='favorites'
        ).count()

        context['to_read_count'] = BookShelf.objects.filter(
            user=user, shelf_type='to_read'
        ).count()

        context['reading_count'] = BookShelf.objects.filter(
            user=user, shelf_type='reading'
        ).count()

        context['read_count'] = BookShelf.objects.filter(
            user=user, shelf_type='read'
        ).count()

        # Prateleiras com livros (limitar a 50 por prateleira)
        context['favorites'] = BookShelf.objects.filter(
            user=user, shelf_type='favorites'
        ).select_related('book', 'book__author', 'book__category')[:50]

        context['to_read'] = BookShelf.objects.filter(
            user=user, shelf_type='to_read'
        ).select_related('book', 'book__author', 'book__category')[:50]

        # Otimização: Prefetch ReadingProgress para evitar N+1 queries
        reading_progress_prefetch = Prefetch(
            'book__reading_progress',
            queryset=ReadingProgress.objects.filter(user=user),
            to_attr='user_progress'
        )

        context['reading'] = BookShelf.objects.filter(
            user=user, shelf_type='reading'
        ).select_related('book', 'book__author', 'book__category').prefetch_related(reading_progress_prefetch)[:50]

        context['read'] = BookShelf.objects.filter(
            user=user, shelf_type='read'
        ).select_related('book', 'book__author', 'book__category')[:50]

        # ========== PRATELEIRAS PERSONALIZADAS (ATUALIZADO) ==========
        custom_shelves_list = []
        custom_shelf_names = []  # <-- Crie esta lista vazia

        if profile:
            shelf_names = profile.get_custom_shelves()
            custom_shelf_names = shelf_names  # <-- Preencha a lista

            for shelf_name in shelf_names:
                # Buscar livros da prateleira (pode estar vazio)
                books = BookShelf.objects.filter(
                    user=user,
                    shelf_type='custom',
                    custom_shelf_name=shelf_name
                ).select_related('book', 'book__author', 'book__category')[:50]

                custom_shelves_list.append({
                    'name': shelf_name,
                    'count': books.count(),
                    'books': books
                })

        context['custom_shelves'] = custom_shelves_list
        # NOVO: Adicione a lista de nomes ao contexto para o modal
        context['custom_shelves_for_modal'] = custom_shelf_names

        # Progressos de leitura ativos (incompletos)
        context['reading_progress'] = ReadingProgress.objects.filter(
            user=user
        ).filter(
            current_page__lt=F('total_pages')
        ).select_related('book', 'book__author').order_by('-last_updated')[:5]

        # Estatísticas de gamificação
        if profile:
            context['total_points'] = profile.total_xp
            context['user_level'] = profile.level
            context['level_name'] = profile.level_name
            context['books_read_this_year'] = profile.books_read_this_year()
            context['reading_goal'] = profile.reading_goal_year
            context['goal_percentage'] = profile.goal_percentage()

            # Novos campos de gamificação
            context['streak_days'] = profile.streak_days
            context['total_badges'] = len(profile.badges) if profile.badges else 0
            context['is_premium'] = profile.is_premium
        else:
            context['total_points'] = 0
            context['user_level'] = 1
            context['level_name'] = 'Leitor Iniciante'
            context['books_read_this_year'] = 0
            context['reading_goal'] = 12
            context['goal_percentage'] = 0
            context['streak_days'] = 0
            context['total_badges'] = 0
            context['is_premium'] = False

        # Avaliações recentes
        context['recent_reviews'] = BookReview.objects.filter(
            user=user
        ).select_related('book').order_by('-created_at')[:5]

        # Atribuir progresso aos itens da prateleira (otimizado com prefetch)
        for shelf_item in context['reading']:
            # O progresso já foi carregado via prefetch_related
            shelf_item.progress = shelf_item.book.user_progress[0] if hasattr(shelf_item.book, 'user_progress') and shelf_item.book.user_progress else None

        # Carregar ou gerar recomendações personalizadas por IA com cache individual por usuário (30 minutos)
        rec_cache_key = f'user_personal_recs_{user.id}'
        personal_recs = cache.get(rec_cache_key)
        if not personal_recs:
            try:
                from recommendations.services.recommendation_service import BookRecommendationService
                from recommendations.services.reader_profile_service import ReaderProfileService
                
                # Atualizar perfil do usuário antes
                ReaderProfileService.update_profile_weights(user)
                profile_obj = ReaderProfileService.generate_profile_summary_ai(user)
                
                raw_recs = BookRecommendationService.get_ai_personalized_recommendations(user, limit=6)
                
                personal_recs = {
                    'profile_biography': profile_obj.profile_summary,
                    'profile_style': profile_obj.reading_style_ai,
                    'books': [{
                        'id': b.id,
                        'title': b.title,
                        'author': {'name': b.author.name} if b.author else {'name': 'Desconhecido'},
                        'cover_image': {'url': b.cover_image.url} if b.cover_image else (b.cover_url_temp if hasattr(b, 'cover_url_temp') else None),
                        'category': {'name': b.category.name} if b.category else None,
                    } for b in raw_recs['books']],
                    'authors': [{
                        'id': a.id,
                        'name': a.name,
                        'photo': {'url': a.photo.url} if a.photo else None,
                    } for a in raw_recs['authors']],
                    'news': [
                        self._serialize_recommended_article(article)
                        for article in raw_recs['news']
                    ],
                    'events': [{
                        'id': e.id,
                        'title': e.title,
                        'banner': {'url': e.banner.url} if e.banner else None,
                        'start_date': e.start_date.strftime('%d/%m/%Y %H:%M') if hasattr(e.start_date, 'strftime') else str(e.start_date),
                        'location': e.location,
                    } for e in raw_recs['events']],
                    'adaptations': [{
                        'id': v.id,
                        'title': v.title,
                        'duration': v.duration,
                        'thumbnail_url': v.thumbnail_url or (v.thumbnail_image.url if v.thumbnail_image else None),
                        'video_url': v.video_url,
                    } for v in raw_recs['adaptations']]
                }
                cache.set(rec_cache_key, personal_recs, 1800)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao injetar recomendações personalizadas na biblioteca: {e}", exc_info=True)
                personal_recs = None
        context['personal_recs'] = personal_recs

        return context
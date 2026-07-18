"""
Selectors do módulo Product Analytics.

Responsabilidade:
- Consultar dados e contagens das tabelas oficiais de outros apps do projeto.
- Evitar duplicação de dados em tabelas do product_analytics.
- Obter contagens agrupadas por data e/ou dimensões básicas (como device, user).
"""
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Importações seguras dos modelos dos outros apps
try:
    from accounts.models import BookShelf, UserProfile
except ImportError:
    BookShelf = None
    UserProfile = None

try:
    from finance.models import Subscription
except ImportError:
    Subscription = None

try:
    from partners.models import AffiliatePartnerClick
except ImportError:
    AffiliatePartnerClick = None

try:
    from chatbot_literario.models import ChatSession
except ImportError:
    ChatSession = None

try:
    from recommendations.models import UserBookInteraction
except ImportError:
    UserBookInteraction = None


class AppSelectors:
    """
    Agrupamento de seletores de dados de outros apps.
    Sempre retorna valores numéricos ou listas simples.
    """

    @staticmethod
    def get_new_users_count(target_date: datetime.date) -> int:
        """Retorna o número de usuários cadastrados na data informada."""
        User = get_user_model()
        # Define o range do dia na timezone local
        start_datetime = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end_datetime = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return User.objects.filter(date_joined__range=(start_datetime, end_datetime)).count()

    @staticmethod
    def get_books_added_count(target_date: datetime.date) -> int:
        """Retorna a contagem de livros adicionados às prateleiras na data informada."""
        if not BookShelf:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return BookShelf.objects.filter(date_added__range=(start, end)).count()

    @staticmethod
    def get_books_completed_count(target_date: datetime.date) -> int:
        """Retorna a contagem de livros finalizados (lidos) na data informada."""
        if not BookShelf:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return BookShelf.objects.filter(
            shelf_type="read",
            finished_reading__range=(start, end)
        ).count()

    @staticmethod
    def get_premium_conversions_count(target_date: datetime.date) -> int:
        """Retorna as conversões premium que iniciaram na data informada."""
        if not Subscription:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return Subscription.objects.filter(
            status="ativa",
            start_date__range=(start, end)
        ).count()

    @staticmethod
    def get_partner_clicks_count(target_date: datetime.date) -> int:
        """Retorna a contagem de cliques em links de afiliados na data informada."""
        if not AffiliatePartnerClick:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return AffiliatePartnerClick.objects.filter(created_at__range=(start, end)).count()

    @staticmethod
    def get_chatbot_sessions_count(target_date: datetime.date) -> int:
        """Retorna o número de sessões criadas de chatbot na data informada."""
        if not ChatSession:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return ChatSession.objects.filter(created_at__range=(start, end)).count()

    @staticmethod
    def get_book_interactions_count(target_date: datetime.date) -> int:
        """Retorna a contagem total de interações livro-usuário em recommendations."""
        if not UserBookInteraction:
            return 0
        start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        return UserBookInteraction.objects.filter(created_at__range=(start, end)).count()

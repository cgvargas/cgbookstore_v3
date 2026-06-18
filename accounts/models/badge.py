"""
Model de Badges (Distintivos) do sistema de gamificação.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.storage_backends import SupabaseMediaStorage


# Raridades dos badges
BADGE_RARITY_CHOICES = [
    ('bronze', '🥉 Bronze'),
    ('silver', '🥈 Prata'),
    ('gold', '🥇 Ouro'),
    ('platinum', '💎 Platina'),
    ('diamond', '💍 Diamante'),
    ('special', '🌟 Especial'),
]


# Categorias de badges
BADGE_CATEGORY_CHOICES = [
    ('reading', '📖 Leitura'),
    ('achievement', '🏆 Conquistas'),
    ('social', '💬 Social'),
    ('time', '⏰ Tempo'),
    ('special_event', '🎉 Evento Especial'),
]


class Badge(models.Model):
    """
    Badges (distintivos) são conquistas visuais que os usuários podem exibir.

    Diferente das Achievements, badges são mais focados em status visual
    e podem ter requisitos mais complexos.
    """

    # ========== CONSTANTES DA CLASSE ==========
    RARITY_CHOICES = BADGE_RARITY_CHOICES
    CATEGORY_CHOICES = BADGE_CATEGORY_CHOICES

    # ========== INFORMAÇÕES BÁSICAS ==========
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Badge",
        help_text="Nome único e descritivo"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="Slug",
        help_text="Identificador único (gerado automaticamente)"
    )

    description = models.TextField(
        max_length=200,
        verbose_name="Descrição",
        help_text="Descrição curta do badge"
    )

    icon = models.CharField(
        max_length=50,
        default='🏅',
        verbose_name="Ícone",
        help_text="Emoji ou código FontAwesome"
    )

    # ========== IMAGEM ==========
    badge_image = models.ImageField(
        upload_to='badges/images/',
        storage=SupabaseMediaStorage(),
        blank=True,
        null=True,
        verbose_name="Imagem do Badge",
        help_text="Imagem visual do badge (recomendado 200x200px)"
    )

    # ========== RARIDADE E CATEGORIA ==========
    rarity = models.CharField(
        max_length=20,
        choices=BADGE_RARITY_CHOICES,
        default='bronze',
        verbose_name="Raridade"
    )

    category = models.CharField(
        max_length=20,
        choices=BADGE_CATEGORY_CHOICES,
        default='reading',
        verbose_name="Categoria"
    )

    # ========== REQUISITOS ==========
    requirements_json = models.JSONField(
        default=dict,
        verbose_name="Requisitos (JSON)",
        help_text="""
        Estrutura flexível para diferentes tipos de requisitos.
        Exemplos:
        - {'achievements_count': 10}
        - {'streak_days': 30}
        - {'books_read_genre': 'terror', 'count': 5}
        - {'ranking_position': 10, 'month': 'any'}
        """
    )

    # ========== METADADOS ==========
    display_order = models.IntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Ordem na listagem (menor = primeiro)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Badge disponível para ser conquistado"
    )

    is_limited_edition = models.BooleanField(
        default=False,
        verbose_name="Edição Limitada",
        help_text="Badge disponível apenas em período limitado"
    )

    available_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Disponível Desde",
        help_text="Data inicial de disponibilidade (opcional)"
    )

    available_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Disponível Até",
        help_text="Data final de disponibilidade (opcional)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado Em"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado Em"
    )

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ['display_order', 'rarity', 'name']
        indexes = [
            models.Index(fields=['rarity', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name} ({self.get_rarity_display()})"

    def save(self, *args, **kwargs):
        """Gera slug automaticamente se não existir."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_rarity_color(self):
        """Retorna a cor associada à raridade."""
        rarity_colors = {
            'bronze': '#cd7f32',
            'silver': '#c0c0c0',
            'gold': '#ffd700',
            'platinum': '#e5e4e2',
            'diamond': '#b9f2ff',
            'special': '#ff1493',
        }
        return rarity_colors.get(self.rarity, '#6c757d')

    def get_rarity_emoji(self):
        """Retorna o emoji da raridade."""
        rarity_emojis = {
            'bronze': '🥉',
            'silver': '🥈',
            'gold': '🥇',
            'platinum': '💎',
            'diamond': '💍',
            'special': '🌟',
        }
        return rarity_emojis.get(self.rarity, '🏅')

    def get_category_emoji(self):
        """Retorna o emoji da categoria."""
        category_emojis = {
            'reading': '📖',
            'achievement': '🏆',
            'social': '💬',
            'time': '⏰',
            'special_event': '🎉',
        }
        return category_emojis.get(self.category, '🏅')

    def is_available_now(self):
        """Verifica se o badge está disponível no momento."""
        if not self.is_active:
            return False

        if not self.is_limited_edition:
            return True

        from django.utils import timezone
        now = timezone.now()

        if self.available_from and now < self.available_from:
            return False

        if self.available_until and now > self.available_until:
            return False

        return True

    def check_requirements(self, user):
        """
        Verifica se o usuário atende aos requisitos para ganhar este badge.

        Args:
            user: Objeto User do Django

        Returns:
            bool: True se requisitos cumpridos, False caso contrário
        """
        if not self.requirements_json:
            return False

        try:
            profile = user.profile
        except:
            return False

        # Verificar diferentes tipos de requisitos

        # Requisito: Assinante Premium
        if 'premium_subscriber' in self.requirements_json:
            if not profile.is_premium_active():
                return False

        # Requisito: Participante de debate
        if 'debate_participant' in self.requirements_json:
            try:
                from debates.models import DebateTopic, DebatePost
                has_topic = DebateTopic.objects.filter(creator=user).exists()
                has_post = DebatePost.objects.filter(author=user, is_deleted=False).exists()
                if not (has_topic or has_post):
                    return False
            except Exception:
                return False

        # Requisito: Participante de quiz
        if 'quiz_participant' in self.requirements_json:
            try:
                from news.models import QuizAttempt
                has_quiz = QuizAttempt.objects.filter(user=user).exists()
                if not has_quiz:
                    return False
            except Exception:
                return False

        # Requisito: Número de conquistas
        if 'achievements_count' in self.requirements_json:
            from .user_achievement import UserAchievement
            count = UserAchievement.objects.filter(
                user=user,
                is_completed=True
            ).count()

            if count < self.requirements_json['achievements_count']:
                return False

        # Requisito: Streak de dias
        if 'streak_days' in self.requirements_json:
            if profile.streak_days < self.requirements_json['streak_days']:
                return False

        # Requisito: Livros lidos de um gênero específico
        if 'books_read_genre' in self.requirements_json:
            from accounts.models import BookShelf
            genre = self.requirements_json['books_read_genre']
            required_count = self.requirements_json.get('count', 1)

            filters = {
                'user': user,
                'shelf_type': 'read'
            }
            if genre and genre != 'any':
                filters['book__category__slug'] = genre

            count = BookShelf.objects.filter(**filters).count()

            if count < required_count:
                return False

        # Requisito: Posição no ranking
        if 'ranking_position' in self.requirements_json:
            from .monthly_ranking import MonthlyRanking
            from datetime import date

            position = self.requirements_json['ranking_position']

            # Buscar ranking do mês atual
            today = date.today()
            try:
                ranking = MonthlyRanking.objects.get(
                    user=user,
                    month=today.month,
                    year=today.year
                )

                if ranking.rank_position > position:
                    return False
            except MonthlyRanking.DoesNotExist:
                return False

        # Se passou por todas as verificações
        return True
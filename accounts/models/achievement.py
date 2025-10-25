"""
Model de Conquistas (Achievements) do sistema de gamificação.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from core.storage_backends import SupabaseMediaStorage


# Categorias de conquistas
ACHIEVEMENT_CATEGORY_CHOICES = [
    ('reading', '📖 Leitura'),
    ('progress', '📊 Progresso'),
    ('social', '💬 Social'),
    ('diversity', '🌈 Diversidade'),
    ('special', '⭐ Especial'),
]


# Níveis de dificuldade
DIFFICULTY_CHOICES = [
    (1, '🟢 Fácil'),
    (2, '🟡 Médio'),
    (3, '🟠 Difícil'),
    (4, '🔴 Muito Difícil'),
    (5, '🟣 Lendário'),
]


class Achievement(models.Model):
    """
    Conquistas disponíveis no sistema.

    Conquistas são objetivos que os usuários podem completar
    para ganhar XP e badges especiais.
    """

    # ========== CONSTANTES DA CLASSE ==========
    CATEGORY_CHOICES = ACHIEVEMENT_CATEGORY_CHOICES
    DIFFICULTY_LEVELS = DIFFICULTY_CHOICES

    # ========== INFORMAÇÕES BÁSICAS ==========
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Conquista",
        help_text="Nome único e descritivo"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="Slug",
        help_text="Identificador único (gerado automaticamente)"
    )

    description = models.TextField(
        max_length=300,
        verbose_name="Descrição",
        help_text="Descrição detalhada da conquista"
    )

    icon = models.CharField(
        max_length=50,
        default='🏆',
        verbose_name="Ícone",
        help_text="Emoji ou código FontAwesome"
    )

    # ========== IMAGEM ==========
    badge_image = models.ImageField(
        upload_to='achievements/badges/',
        storage=SupabaseMediaStorage(),
        blank=True,
        null=True,
        verbose_name="Imagem do Badge",
        help_text="Imagem visual da conquista (opcional)"
    )

    # ========== GAMIFICAÇÃO ==========
    xp_reward = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        verbose_name="Recompensa em XP",
        help_text="Quantidade de XP concedida ao completar"
    )

    category = models.CharField(
        max_length=20,
        choices=ACHIEVEMENT_CATEGORY_CHOICES,
        default='reading',
        verbose_name="Categoria"
    )

    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=2,
        verbose_name="Dificuldade"
    )

    # ========== REQUISITOS ==========
    requirements_json = models.JSONField(
        default=dict,
        verbose_name="Requisitos (JSON)",
        help_text="""
        Estrutura: {
            'type': 'books_read' | 'pages_read' | 'streak_days' | 'reviews_written' | 'categories_read',
            'value': <número>,
            'condition': 'greater_or_equal' | 'equal' | 'less_or_equal'
        }
        """
    )

    # ========== STATUS ==========
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Conquista disponível para ser completada"
    )

    display_order = models.IntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Ordem na listagem (menor = primeiro)"
    )

    # ========== METADADOS ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado Em"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado Em"
    )

    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"
        ordering = ['display_order', 'difficulty_level', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['difficulty_level']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name}"

    def save(self, *args, **kwargs):
        """Gera slug automaticamente se não existir."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_category_display_emoji(self):
        """Retorna o emoji da categoria."""
        category_emojis = {
            'reading': '📖',
            'progress': '📊',
            'social': '💬',
            'diversity': '🌈',
            'special': '⭐',
        }
        return category_emojis.get(self.category, '🏆')

    def get_difficulty_color(self):
        """Retorna a cor associada à dificuldade."""
        difficulty_colors = {
            1: '#28a745',  # Verde
            2: '#ffc107',  # Amarelo
            3: '#fd7e14',  # Laranja
            4: '#dc3545',  # Vermelho
            5: '#6f42c1',  # Roxo
        }
        return difficulty_colors.get(self.difficulty_level, '#6c757d')

    def is_requirement_met(self, user):
        """
        Verifica se o usuário cumpre os requisitos da conquista.

        Args:
            user: Objeto User do Django

        Returns:
            bool: True se requisitos cumpridos, False caso contrário
        """
        if not self.requirements_json:
            return False

        req_type = self.requirements_json.get('type')
        req_value = self.requirements_json.get('value', 0)
        condition = self.requirements_json.get('condition', 'greater_or_equal')

        # Buscar perfil do usuário
        try:
            profile = user.profile
        except:
            return False

        # Verificar tipo de requisito
        user_value = 0

        if req_type == 'books_read':
            user_value = profile.books_read_count
        elif req_type == 'pages_read':
            user_value = profile.total_pages_read
        elif req_type == 'streak_days':
            user_value = profile.streak_days
        elif req_type == 'reviews_written':
            from accounts.models import BookReview
            user_value = BookReview.objects.filter(user=user).count()
        elif req_type == 'categories_read':
            from accounts.models import BookShelf
            user_value = BookShelf.objects.filter(
                user=user,
                shelf_type='read'
            ).values('book__category').distinct().count()
        else:
            return False

        # Verificar condição
        if condition == 'greater_or_equal':
            return user_value >= req_value
        elif condition == 'equal':
            return user_value == req_value
        elif condition == 'less_or_equal':
            return user_value <= req_value

        return False

    def calculate_progress(self, user):
        """
        Calcula a porcentagem de progresso do usuário nesta conquista.

        Args:
            user: Objeto User do Django

        Returns:
            int: Porcentagem de progresso (0-100)
        """
        if not self.requirements_json:
            return 0

        req_type = self.requirements_json.get('type')
        req_value = self.requirements_json.get('value', 0)

        if req_value == 0:
            return 0

        try:
            profile = user.profile
        except:
            return 0

        user_value = 0

        if req_type == 'books_read':
            user_value = profile.books_read_count
        elif req_type == 'pages_read':
            user_value = profile.total_pages_read
        elif req_type == 'streak_days':
            user_value = profile.streak_days
        elif req_type == 'reviews_written':
            from accounts.models import BookReview
            user_value = BookReview.objects.filter(user=user).count()
        elif req_type == 'categories_read':
            from accounts.models import BookShelf
            user_value = BookShelf.objects.filter(
                user=user,
                shelf_type='read'
            ).values('book__category').distinct().count()

        # Calcular porcentagem
        percentage = min(100, int((user_value / req_value) * 100))
        return percentage
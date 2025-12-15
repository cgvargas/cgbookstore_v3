"""
Model de Perfil de Usuário expandido com gamificação e personalização.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Category
from core.storage_backends import SupabaseMediaStorage
import math


# Opções de temas disponíveis
THEME_CHOICES = [
    # SEM TEMA (Padrão)
    ('none', '⚪ Sem Tema (Padrão Sistema)'),

    # FREE (3 temas)
    ('fantasy', '✨ Fantasia (Roxo/Dourado)'),
    ('classic', '📚 Clássicos (Marrom/Bege)'),
    ('romance', '💕 Romance (Rosa/Vermelho)'),

    # PREMIUM (12 temas)
    ('scifi', '🚀 Ficção Científica (Azul Neon/Prateado) - PREMIUM'),
    ('horror', '🎃 Terror (Vermelho Escuro/Preto) - PREMIUM'),
    ('mystery', '🔍 Mistério (Verde Escuro/Cinza) - PREMIUM'),
    ('biography', '📖 Biografia (Azul Royal/Dourado) - PREMIUM'),
    ('poetry', '🌸 Poesia (Lilás/Rosa Claro) - PREMIUM'),
    ('adventure', '🗺️ Aventura (Laranja/Marrom) - PREMIUM'),
    ('thriller', '🔪 Thriller (Vermelho/Preto) - PREMIUM'),
    ('historical', '🏛️ Histórico (Dourado/Marrom) - PREMIUM'),
    ('selfhelp', '💡 Autoajuda (Amarelo/Laranja) - PREMIUM'),
    ('philosophy', '🧠 Filosofia (Azul Escuro/Cinza) - PREMIUM'),
    ('dystopian', '🌆 Distopia (Cinza/Vermelho) - PREMIUM'),
    ('contemporary', '🎨 Contemporâneo (Multicolor) - PREMIUM'),
]


class UserProfile(models.Model):
    """
    Perfil estendido do usuário com gamificação, personalização e biblioteca.
    """

    # ========== RELACIONAMENTO ==========
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuário"
    )

    # ========== PERSONALIZAÇÃO VISUAL ==========
    avatar = models.ImageField(
        upload_to='users/avatars/',
        storage=SupabaseMediaStorage(),
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Foto de perfil (máx. 5MB, 500x500px)"
    )

    @property
    def cached_avatar_url(self):
        """
        Retorna URL do avatar usando cache para memória (5 min).
        Evita chamada de rede bloqueante do SupabaseStorage.url em cada request.
        """
        if not self.avatar:
            return None
            
        from django.core.cache import cache
        cache_key = f"user_avatar_url_{self.user.id}"
        url = cache.get(cache_key)
        
        if not url:
            try:
                # Gera URL (blocking network call)
                url = self.avatar.url
                # Cache por 5 minutos
                cache.set(cache_key, url, 300)
            except Exception:
                return None
                
        return url

    banner = models.ImageField(
        upload_to='users/banners/',
        storage=SupabaseMediaStorage(),
        blank=True,
        null=True,
        verbose_name="Banner",
        help_text="Banner personalizado (máx. 5MB, 1200x300px)"
    )

    # ========== BACKGROUND CUSTOMIZADO (PREMIUM) ==========
    custom_background = models.ImageField(
        upload_to='users/backgrounds/',
        storage=SupabaseMediaStorage(),
        blank=True,
        null=True,
        verbose_name="Background Personalizado",
        help_text="Imagem de fundo personalizada para a biblioteca (máx. 10MB, apenas PREMIUM)"
    )

    background_style = models.CharField(
        max_length=10,
        choices=[
            ('cover', 'Cobrir (Cover)'),
            ('contain', 'Conter (Contain)'),
            ('repeat', 'Repetir (Repeat)'),
        ],
        default='cover',
        verbose_name="Estilo do Background",
        help_text="Como a imagem de fundo deve ser exibida"
    )

    background_opacity = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Opacidade do Overlay",
        help_text="Opacidade da camada escura sobre o background (0=transparente, 100=opaco)"
    )

    bio = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Bio Literária",
        help_text="Descreva seu perfil de leitor em até 150 caracteres"
    )

    theme_preference = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='none',
        verbose_name="Tema Visual",
        help_text="Tema de personalização da biblioteca"
    )

    favorite_genre = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='favorite_of_users',
        verbose_name="Gênero Favorito"
    )

    # ========== GAMIFICAÇÃO ==========
    total_xp = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="XP Total",
        help_text="Pontos de experiência acumulados"
    )

    level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name="Nível",
        help_text="Nível atual (1-30)"
    )

    badges = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Badges Conquistados",
        help_text="Lista de IDs de badges conquistados"
    )

    custom_shelves_list = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Prateleiras Personalizadas",
        help_text="Lista de nomes de prateleiras personalizadas criadas pelo usuário"
    )

    streak_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Dias de Streak",
        help_text="Dias consecutivos com atividade"
    )

    last_activity_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Última Atividade"
    )

    # ========== METAS E ESTATÍSTICAS ==========
    reading_goal_year = models.IntegerField(
        default=12,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name="Meta Anual de Leitura",
        help_text="Quantos livros deseja ler este ano?"
    )

    books_read_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Livros Lidos",
        help_text="Total de livros concluídos"
    )

    total_pages_read = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Páginas Lidas",
        help_text="Total de páginas lidas"
    )

    # ========== PLANO E ASSINATURA ==========
    is_premium = models.BooleanField(
        default=False,
        verbose_name="Usuário Premium"
    )

    premium_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Premium Expira Em"
    )

    # ========== SOCIAL ==========
    is_profile_public = models.BooleanField(
        default=True,
        verbose_name="Perfil Público",
        help_text="Permitir que outros usuários vejam seu perfil"
    )

    allow_followers = models.BooleanField(
        default=True,
        verbose_name="Permitir Seguidores"
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
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        ordering = ['-total_xp']

    def __str__(self):
        return f"Perfil de {self.user.username}"

    # ========== MÉTODOS DE GAMIFICAÇÃO ==========

    def calculate_level(self):
        """
        Calcula o nível baseado no XP total.
        Fórmula: Nível = √(XP / 100)
        """
        if self.total_xp == 0:
            return 1

        calculated_level = int((self.total_xp / 100) ** 0.5) + 1
        return min(calculated_level, 30)  # Máximo nível 30

    @property
    def xp_for_next_level(self):
        """Retorna quanto XP falta para o próximo nível."""
        current_level = self.level
        next_level_xp = ((current_level) ** 2) * 100
        return max(0, next_level_xp - self.total_xp)

    def xp_percentage_to_next_level(self):
        """Retorna a porcentagem de progresso até o próximo nível."""
        current_level_xp = ((self.level - 1) ** 2) * 100
        next_level_xp = ((self.level) ** 2) * 100
        xp_in_current_level = self.total_xp - current_level_xp
        xp_needed_for_level = next_level_xp - current_level_xp

        if xp_needed_for_level == 0:
            return 100

        percentage = (xp_in_current_level / xp_needed_for_level) * 100
        return min(100, max(0, percentage))

    @property  # ✅ ADICIONADO
    def xp_progress_percentage(self):
        """Alias para xp_percentage_to_next_level (compatibilidade com views)."""
        return self.xp_percentage_to_next_level()

    @property
    def level_name(self):
        """Retorna o nome do nível baseado no número."""
        level_names = {
            1: "📖 Aprendiz",
            3: "📚 Leitor",
            5: "📗 Leitor Ávido",
            7: "📘 Conhecedor",
            10: "📙 Bibliófilo",
            12: "📕 Literato",
            15: "🎓 Erudito",
            18: "🏆 Expert Literário",
            20: "⭐ Mestre das Letras",
            23: "👑 Grande Autor",
            25: "🔮 Sábio Literário",
            27: "💎 Guardião dos Livros",
            30: "🌟 Lenda Literária"
        }

        # Encontra o nome mais próximo sem ultrapassar
        for level_threshold in sorted(level_names.keys(), reverse=True):
            if self.level >= level_threshold:
                return level_names[level_threshold]

        return "📖 Aprendiz"

    def add_xp(self, amount):
        """
        Adiciona XP e verifica se subiu de nível.
        Retorna: (novo_level, subiu_de_nivel)
        """
        old_level = self.level
        self.total_xp += amount

        # Recalcula nível
        new_level = self.calculate_level()
        leveled_up = new_level > old_level

        if leveled_up:
            self.level = new_level

        self.save()

        return (new_level, leveled_up)

    def has_badge(self, badge_id):
        """Verifica se o usuário possui um badge específico."""
        return badge_id in self.badges

    def award_badge(self, badge_id):
        """Concede um badge ao usuário."""
        if not self.has_badge(badge_id):
            self.badges.append(badge_id)
            self.save()
            return True
        return False

    def update_streak(self):
        """
        Atualiza o streak de leitura.
        Deve ser chamado quando o usuário tem atividade.
        """
        from datetime import date
        today = date.today()

        if self.last_activity_date is None:
            # Primeira atividade
            self.streak_days = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Já registrou atividade hoje
            pass
        elif (today - self.last_activity_date).days == 1:
            # Atividade consecutiva (ontem → hoje)
            self.streak_days += 1
            self.last_activity_date = today
        else:
            # Quebrou o streak
            self.streak_days = 1
            self.last_activity_date = today

        self.save()
        return self.streak_days

    def reset_streak(self):
        """Reseta o streak para 0."""
        self.streak_days = 0
        self.save()

    def is_premium_active(self):
        """
        Verifica se o plano premium do usuário está ativo.
        Retorna True se for premium e a data de expiração for futura ou nula.
        """
        if not self.is_premium:
            return False

        if self.premium_expires_at is None:
            return True  # Assinatura vitalícia

        from django.utils import timezone
        return timezone.now() < self.premium_expires_at

    def can_use_premium_feature(self):
        """Verifica se pode usar funcionalidades premium."""
        return self.is_premium_active()

    # ========== MÉTODOS DE ESTATÍSTICAS ==========

    def books_read_this_year(self):
        """Retorna quantos livros leu este ano."""
        from datetime import date
        from accounts.models import BookShelf # O import está correto aqui

        current_year = date.today().year

        # CORREÇÃO: Usar 'finished_reading__year' ao invés de 'created_at__year'
        return BookShelf.objects.filter(
            user=self.user,
            shelf_type='read',
            finished_reading__year=current_year # LINHA CORRIGIDA
        ).count()

    def goal_percentage(self):
        """Retorna a porcentagem da meta anual alcançada."""
        books_read = self.books_read_this_year()
        if self.reading_goal_year == 0:
            return 0

        percentage = (books_read / self.reading_goal_year) * 100
        return min(100, percentage)

    def average_pages_per_book(self):
        """Retorna a média de páginas por livro lido."""
        if self.books_read_count == 0:
            return 0
        return self.total_pages_read // self.books_read_count

    def add_custom_shelf(self, shelf_name):
        """
        Adiciona uma prateleira personalizada à lista do usuário.

        Args:
            shelf_name (str): Nome da prateleira

        Returns:
            bool: True se adicionou, False se já existia
        """
        shelf_name = shelf_name.strip()

        if not shelf_name:
            return False

        # Verificar se já existe
        if shelf_name in self.custom_shelves_list:
            return False

        # Adicionar à lista
        self.custom_shelves_list.append(shelf_name)
        self.save()
        return True

    def remove_custom_shelf(self, shelf_name):
        """
        Remove uma prateleira personalizada da lista.

        Args:
            shelf_name (str): Nome da prateleira

        Returns:
            bool: True se removeu, False se não existia
        """
        if shelf_name in self.custom_shelves_list:
            self.custom_shelves_list.remove(shelf_name)
            self.save()
            return True
        return False

    def has_custom_shelf(self, shelf_name):
        """
        Verifica se uma prateleira personalizada existe.

        Args:
            shelf_name (str): Nome da prateleira

        Returns:
            bool: True se existe, False caso contrário
        """
        return shelf_name in self.custom_shelves_list

    def get_custom_shelves(self):
        """
        Retorna lista de prateleiras personalizadas ordenada alfabeticamente.

        Returns:
            list: Lista de nomes de prateleiras
        """
        return sorted(self.custom_shelves_list)
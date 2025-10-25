"""
Model de Ranking Mensal do sistema de gamificação.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class MonthlyRanking(models.Model):
    """
    Ranking mensal de leitores.

    Rastreia o desempenho dos usuários mês a mês e calcula posições no ranking.
    """

    # ========== IDENTIFICAÇÃO ==========
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monthly_rankings',
        verbose_name="Usuário"
    )

    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Mês",
        help_text="Mês do ranking (1-12)"
    )

    year = models.IntegerField(
        verbose_name="Ano",
        help_text="Ano do ranking"
    )

    # ========== ESTATÍSTICAS ==========
    total_xp = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="XP Total do Mês",
        help_text="XP ganho durante este mês"
    )

    books_read = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Livros Lidos",
        help_text="Livros finalizados no mês"
    )

    pages_read = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Páginas Lidas",
        help_text="Total de páginas lidas no mês"
    )

    reviews_written = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Reviews Escritas",
        help_text="Reviews publicadas no mês"
    )

    achievements_earned = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Conquistas Desbloqueadas",
        help_text="Conquistas completadas no mês"
    )

    consecutive_reading_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Dias Consecutivos de Leitura",
        help_text="Maior streak de dias de leitura no mês"
    )

    # ========== PONTUAÇÃO E RANKING ==========
    total_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Pontuação Total",
        help_text="Pontuação calculada para ranking"
    )

    rank_position = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Posição no Ranking",
        help_text="Posição atual no ranking mensal (0 = não ranqueado)"
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
        verbose_name = "Ranking Mensal"
        verbose_name_plural = "Rankings Mensais"
        unique_together = ['user', 'month', 'year']
        ordering = ['year', 'month', 'rank_position']
        indexes = [
            models.Index(fields=['month', 'year', 'rank_position']),
            models.Index(fields=['total_score']),
        ]

    def __str__(self):
        position_display = f"#{self.rank_position}" if self.rank_position > 0 else "Não Ranqueado"
        return f"{self.user.username} - {self.month}/{self.year} - {position_display}"

    def calculate_score(self):
        """
        Calcula a pontuação total baseada nas estatísticas.

        Fórmula:
        - Livros lidos: 100 pontos cada
        - Páginas lidas: 1 ponto por página
        - Reviews escritas: 50 pontos cada
        - Conquistas desbloqueadas: XP da conquista
        - Dias consecutivos: 10 pontos por dia

        Returns:
            int: Pontuação calculada
        """
        score = 0

        # Livros lidos (100 pontos cada)
        score += self.books_read * 100

        # Páginas lidas (1 ponto por página)
        score += self.pages_read

        # Reviews (50 pontos cada)
        score += self.reviews_written * 50

        # XP do mês
        score += self.total_xp

        # Streak de dias (10 pontos por dia)
        score += self.consecutive_reading_days * 10

        self.total_score = score
        self.save()

        return score

    def update_statistics(self):
        """
        Atualiza as estatísticas deste ranking baseado nas ações do usuário no mês.
        """
        from datetime import datetime
        from accounts.models import BookShelf, BookReview, UserAchievement

        # Construir datas de início e fim do mês
        start_date = datetime(self.year, self.month, 1)

        if self.month == 12:
            end_date = datetime(self.year + 1, 1, 1)
        else:
            end_date = datetime(self.year, self.month + 1, 1)

        # Livros lidos no mês
        self.books_read = BookShelf.objects.filter(
            user=self.user,
            shelf_type='read',
            finished_reading__gte=start_date,
            finished_reading__lt=end_date
        ).count()

        # Reviews escritas no mês
        self.reviews_written = BookReview.objects.filter(
            user=self.user,
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()

        # Conquistas desbloqueadas no mês
        self.achievements_earned = UserAchievement.objects.filter(
            user=self.user,
            is_completed=True,
            earned_at__gte=start_date,
            earned_at__lt=end_date
        ).count()

        # Páginas lidas (aproximação baseada em livros finalizados)
        finished_books = BookShelf.objects.filter(
            user=self.user,
            shelf_type='read',
            finished_reading__gte=start_date,
            finished_reading__lt=end_date
        ).select_related('book')

        self.pages_read = sum(
            book_shelf.book.num_pages or 0
            for book_shelf in finished_books
        )

        # XP do mês (calculado a partir do perfil)
        # Nota: Isto é uma aproximação. Idealmente, haveria um log de XP ganho.
        # Por simplicidade, usaremos as conquistas desbloqueadas no mês
        earned_achievements = UserAchievement.objects.filter(
            user=self.user,
            is_completed=True,
            earned_at__gte=start_date,
            earned_at__lt=end_date
        ).select_related('achievement')

        self.total_xp = sum(
            ua.achievement.xp_reward
            for ua in earned_achievements
        )

        # Calcular pontuação
        self.calculate_score()

        self.save()

    @classmethod
    def get_or_create_current(cls, user):
        """
        Busca ou cria o ranking do mês atual para um usuário.

        Args:
            user: Objeto User

        Returns:
            MonthlyRanking: Instância do ranking
        """
        from datetime import date
        today = date.today()

        ranking, created = cls.objects.get_or_create(
            user=user,
            month=today.month,
            year=today.year
        )

        if not created:
            ranking.update_statistics()

        return ranking

    @classmethod
    def update_all_rankings(cls, month=None, year=None):
        """
        Atualiza todos os rankings de um mês e recalcula posições.

        Args:
            month: Mês específico (None = mês atual)
            year: Ano específico (None = ano atual)

        Returns:
            int: Número de rankings atualizados
        """
        from datetime import date

        if month is None or year is None:
            today = date.today()
            month = month or today.month
            year = year or today.year

        # Buscar todos os rankings do mês
        rankings = cls.objects.filter(month=month, year=year)

        # Atualizar estatísticas de cada um
        for ranking in rankings:
            ranking.update_statistics()

        # Recalcular posições
        rankings = rankings.order_by('-total_score', 'user__username')

        for position, ranking in enumerate(rankings, start=1):
            ranking.rank_position = position
            ranking.save()

        return rankings.count()

    @classmethod
    def get_top_n(cls, month=None, year=None, limit=10):
        """
        Retorna o top N de um mês específico.

        Args:
            month: Mês (None = mês atual)
            year: Ano (None = ano atual)
            limit: Número de posições (padrão: 10)

        Returns:
            QuerySet: Top N rankings ordenados
        """
        from datetime import date

        if month is None or year is None:
            today = date.today()
            month = month or today.month
            year = year or today.year

        return cls.objects.filter(
            month=month,
            year=year,
            rank_position__gt=0
        ).select_related('user', 'user__profile').order_by('rank_position')[:limit]

    def get_position_display(self):
        """Retorna a posição com emoji."""
        if self.rank_position == 1:
            return "🥇 1º Lugar"
        elif self.rank_position == 2:
            return "🥈 2º Lugar"
        elif self.rank_position == 3:
            return "🥉 3º Lugar"
        elif self.rank_position <= 10:
            return f"🏅 {self.rank_position}º Lugar"
        elif self.rank_position > 0:
            return f"#{self.rank_position}"
        else:
            return "Não Ranqueado"
"""
Model de Conquistas do Usuário (UserAchievement).
Representa conquistas que os usuários completaram ou estão progredindo.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .achievement import Achievement


class UserAchievement(models.Model):
    """
    Conquistas conquistadas ou em progresso pelos usuários.

    Relaciona usuários com conquistas e rastreia progresso.
    """

    # ========== RELACIONAMENTOS ==========
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name="Usuário"
    )

    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name="Conquista"
    )

    # ========== PROGRESSO ==========
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Progresso (%)",
        help_text="Porcentagem de conclusão (0-100)"
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name="Completada",
        help_text="True se a conquista foi completada"
    )

    # ========== DATAS ==========
    earned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Conquistada Em",
        help_text="Data/hora que completou a conquista"
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
        verbose_name = "Conquista do Usuário"
        verbose_name_plural = "Conquistas dos Usuários"
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at', '-progress_percentage']
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['achievement', 'is_completed']),
        ]

    def __str__(self):
        status = "✅" if self.is_completed else f"🔄 {self.progress_percentage}%"
        return f"{self.user.username} - {self.achievement.name} {status}"

    def update_progress(self):
        """
        Atualiza o progresso desta conquista baseado nas estatísticas atuais do usuário.

        Returns:
            bool: True se a conquista foi completada, False caso contrário
        """
        if self.is_completed:
            return True

        # Calcular progresso atual
        self.progress_percentage = self.achievement.calculate_progress(self.user)

        # Verificar se completou
        if self.achievement.is_requirement_met(self.user):
            self.complete()
            return True

        self.save()
        return False

    def complete(self):
        """
        Marca a conquista como completada e concede recompensas.
        """
        if self.is_completed:
            return

        from django.utils import timezone

        self.is_completed = True
        self.progress_percentage = 100
        self.earned_at = timezone.now()

        # Conceder XP ao usuário
        profile = self.user.profile
        old_level, leveled_up = profile.add_xp(self.achievement.xp_reward)

        # Criar notificação
        from accounts.models import SystemNotification

        message = f"🎉 Parabéns! Você conquistou: {self.achievement.name}! +{self.achievement.xp_reward} XP"

        if leveled_up:
            message += f" e subiu para o nível {profile.level}! 🎊"

        SystemNotification.objects.create(
            user=self.user,
            notification_type='achievement_unlocked',
            message=message,
            priority=2,
            is_read=False
        )

        self.save()

    def get_progress_display(self):
        """Retorna string formatada do progresso."""
        if self.is_completed:
            return "✅ Completada"
        else:
            return f"🔄 {self.progress_percentage}%"

    @classmethod
    def create_or_update(cls, user, achievement):
        """
        Cria ou atualiza uma UserAchievement.

        Args:
            user: Objeto User
            achievement: Objeto Achievement

        Returns:
            UserAchievement: Instância criada ou atualizada
        """
        user_achievement, created = cls.objects.get_or_create(
            user=user,
            achievement=achievement
        )

        if not created:
            user_achievement.update_progress()

        return user_achievement

    @classmethod
    def check_and_award_achievements(cls, user):
        """
        Verifica todas as conquistas disponíveis e concede as que o usuário completou.

        Args:
            user: Objeto User

        Returns:
            list: Lista de conquistas recém-concedidas
        """
        from .achievement import Achievement

        newly_awarded = []

        # Buscar todas as conquistas ativas
        achievements = Achievement.objects.filter(is_active=True)

        for achievement in achievements:
            # Criar ou buscar UserAchievement
            user_achievement, created = cls.objects.get_or_create(
                user=user,
                achievement=achievement
            )

            # Se já completada, pular
            if user_achievement.is_completed:
                continue

            # Atualizar progresso
            completed = user_achievement.update_progress()

            if completed and user_achievement.is_completed:
                newly_awarded.append(user_achievement)

        return newly_awarded
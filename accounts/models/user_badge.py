"""
Model de Badges do Usuário (UserBadge).
Representa badges que os usuários conquistaram.
"""

from django.db import models
from django.contrib.auth.models import User
from .badge import Badge


class UserBadge(models.Model):
    """
    Badges conquistados pelos usuários.

    Relaciona usuários com badges e permite showcase (exibir no perfil).
    """

    # ========== RELACIONAMENTOS ==========
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_badges',
        verbose_name="Usuário"
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='user_badges',
        verbose_name="Badge"
    )

    # ========== SHOWCASE ==========
    is_showcased = models.BooleanField(
        default=False,
        verbose_name="Exibir no Perfil",
        help_text="Badge será exibido no perfil do usuário"
    )

    showcase_order = models.IntegerField(
        default=0,
        verbose_name="Ordem de Exibição",
        help_text="Ordem no showcase (menor = primeiro)"
    )

    # ========== METADADOS ==========
    earned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Conquistado Em"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado Em"
    )

    class Meta:
        verbose_name = "Badge do Usuário"
        verbose_name_plural = "Badges dos Usuários"
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', 'is_showcased']),
            models.Index(fields=['badge']),
        ]

    def __str__(self):
        showcase = "⭐" if self.is_showcased else ""
        return f"{showcase} {self.user.username} - {self.badge.name}"

    @classmethod
    def award_badge(cls, user, badge):
        """
        Concede um badge a um usuário.

        Args:
            user: Objeto User
            badge: Objeto Badge

        Returns:
            tuple: (UserBadge, created) onde created é True se foi criado
        """
        user_badge, created = cls.objects.get_or_create(
            user=user,
            badge=badge
        )

        if created:
            # Criar notificação
            from accounts.models import SystemNotification

            rarity_emoji = badge.get_rarity_emoji()

            SystemNotification.objects.create(
                user=user,
                notification_type='badge_earned',
                message=f"{rarity_emoji} Você ganhou o badge: {badge.name}!",
                priority=2,
                is_read=False
            )

        return user_badge, created

    @classmethod
    def get_showcased_badges(cls, user, limit=3):
        """
        Retorna os badges que o usuário está exibindo no perfil.

        Args:
            user: Objeto User
            limit: Número máximo de badges (padrão: 3)

        Returns:
            QuerySet: Badges showcaseados ordenados
        """
        return cls.objects.filter(
            user=user,
            is_showcased=True
        ).select_related('badge').order_by('showcase_order', '-earned_at')[:limit]

    @classmethod
    def set_showcase(cls, user, badge_ids):
        """
        Define quais badges serão exibidos no perfil do usuário.

        Args:
            user: Objeto User
            badge_ids: Lista de IDs de badges para showcase

        Returns:
            int: Número de badges configurados
        """
        # Remover showcase de todos os badges
        cls.objects.filter(user=user).update(
            is_showcased=False,
            showcase_order=0
        )

        # Configurar novos badges
        for index, badge_id in enumerate(badge_ids[:3], start=1):
            try:
                user_badge = cls.objects.get(user=user, badge_id=badge_id)
                user_badge.is_showcased = True
                user_badge.showcase_order = index
                user_badge.save()
            except cls.DoesNotExist:
                continue

        return min(len(badge_ids), 3)

    @classmethod
    def check_and_award_badges(cls, user):
        """
        Verifica todos os badges disponíveis e concede os que o usuário merece.

        Args:
            user: Objeto User

        Returns:
            list: Lista de badges recém-concedidos
        """
        from .badge import Badge

        newly_awarded = []

        # Buscar todos os badges ativos e disponíveis
        badges = Badge.objects.filter(is_active=True)

        for badge in badges:
            # Verificar se já possui o badge
            if cls.objects.filter(user=user, badge=badge).exists():
                continue

            # Verificar se está disponível agora
            if not badge.is_available_now():
                continue

            # Verificar requisitos
            if badge.check_requirements(user):
                user_badge, created = cls.award_badge(user, badge)
                if created:
                    newly_awarded.append(user_badge)

        return newly_awarded

    def get_rarity_display(self):
        """Retorna a raridade do badge com emoji."""
        return f"{self.badge.get_rarity_emoji()} {self.badge.get_rarity_display()}"
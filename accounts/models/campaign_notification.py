"""
Modelo de Notificações de Campanhas
CGBookStore v3

Notificações enviadas quando usuários recebem Premium via campanha de marketing.
"""

from django.db import models
from django.utils import timezone
from .base_notification import BaseNotification


class CampaignNotification(BaseNotification):
    """
    Notificação enviada quando um usuário recebe Premium via campanha.

    Herda de BaseNotification para integração com o sistema de notificações.
    """

    # Tipos de notificações de campanha
    NOTIFICATION_TYPES = [
        ('premium_granted', 'Premium Concedido'),
        ('premium_expiring', 'Premium Expirando'),
        ('premium_expired', 'Premium Expirado'),
    ]

    # Referência à campanha (opcional - pode ser None se campanha for deletada)
    campaign = models.ForeignKey(
        'finance.Campaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Campanha',
        related_name='notifications'
    )

    # Referência à concessão
    campaign_grant = models.ForeignKey(
        'finance.CampaignGrant',
        on_delete=models.CASCADE,
        verbose_name='Concessão',
        related_name='notifications'
    )

    class Meta:
        verbose_name = 'Notificação de Campanha'
        verbose_name_plural = 'Notificações de Campanhas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notification_type', '-created_at']),
            models.Index(fields=['campaign', '-created_at']),
        ]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        campaign_name = self.campaign.name if self.campaign else "Campanha Removida"
        return f'[{status}] {self.user.username} - {campaign_name}'

    @classmethod
    def create_premium_granted_notification(cls, user, campaign, grant):
        """
        Cria notificação de Premium concedido.

        Args:
            user: Usuário que recebeu
            campaign: Campanha que concedeu
            grant: CampaignGrant criado

        Returns:
            CampaignNotification criada
        """
        message = (
            f"🎉 Parabéns! Você recebeu {campaign.duration_days} dias de Premium "
            f"através da campanha '{campaign.name}'!"
        )

        notification = cls.objects.create(
            user=user,
            campaign=campaign,
            campaign_grant=grant,
            notification_type='premium_granted',
            message=message,
            priority=2,  # Média
            action_url='/finance/subscription/status/',
            action_text='Ver Meu Premium',
            extra_data={
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'duration_days': campaign.duration_days,
                'expires_at': grant.expires_at.isoformat(),
            }
        )

        return notification

    @classmethod
    def create_expiring_notification(cls, user, grant):
        """
        Cria notificação de Premium expirando em breve.

        Args:
            user: Usuário
            grant: CampaignGrant que está expirando

        Returns:
            CampaignNotification criada
        """
        campaign_name = grant.campaign.name if grant.campaign else "Campanha"
        days_left = (grant.expires_at - timezone.now()).days

        # Mensagem personalizada baseada em dias restantes
        if days_left <= 0:
            message = (
                f"🚨 Seu Premium da campanha '{campaign_name}' expira HOJE! "
                f"Renove agora para não perder o acesso."
            )
        elif days_left == 1:
            message = (
                f"⚠️ Seu Premium da campanha '{campaign_name}' expira AMANHÃ! "
                f"Não perca tempo, renove agora."
            )
        elif days_left <= 3:
            message = (
                f"⏰ Seu Premium da campanha '{campaign_name}' expira em {days_left} dias. "
                f"Garanta sua renovação!"
            )
        else:
            message = (
                f"ℹ️ Seu Premium da campanha '{campaign_name}' expira em {days_left} dias. "
                f"Aproveite os benefícios enquanto pode!"
            )

        notification = cls.objects.create(
            user=user,
            campaign=grant.campaign,
            campaign_grant=grant,
            notification_type='premium_expiring',
            message=message,
            priority=2,
            action_url='/finance/subscription/checkout/',
            action_text='Renovar Premium',
            extra_data={
                'days_left': days_left,
                'expires_at': grant.expires_at.isoformat(),
            }
        )

        return notification


# ========== REGISTRO NO SISTEMA ==========

from .base_notification import NotificationRegistry

# Registrar CampaignNotification no sistema unificado
NotificationRegistry.register('campaign', CampaignNotification, {
    'category_name': 'Campanhas',
    'icon': 'fas fa-gift',
    'color': '#9C27B0'
})

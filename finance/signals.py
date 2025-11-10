from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Subscription, Order, Campaign, CampaignGrant
from .services import CampaignService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def subscription_status_changed(sender, instance, created, **kwargs):
    """
    Sincroniza Subscription com UserProfile quando o status muda
    """
    try:
        # Tenta obter ou criar UserProfile
        from accounts.models import UserProfile
        profile, profile_created = UserProfile.objects.get_or_create(user=instance.user)

        if profile_created:
            logger.info(f"UserProfile criado automaticamente para {instance.user.username}")

        if instance.is_active():
            profile.is_premium = True
            profile.premium_expires_at = instance.expiration_date
        else:
            # Se a assinatura não está ativa, verifica se há concessão de campanha ativa
            active_grant = CampaignGrant.objects.filter(
                user=instance.user,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()

            if not active_grant:
                profile.is_premium = False
                profile.premium_expires_at = None

        profile.save()
        logger.info(f"UserProfile sincronizado para {instance.user.username}")
    except Exception as e:
        logger.error(f"Erro ao sincronizar UserProfile: {str(e)}")


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Processa mudanças de status em pedidos
    """
    # Placeholder para lógica futura de pedidos
    pass


@receiver(post_save, sender=User)
def check_new_user_campaigns(sender, instance, created, **kwargs):
    """
    Verifica se há campanhas ativas para novos usuários
    """
    if not created:
        return

    try:
        # Busca campanhas ativas para novos usuários
        now = timezone.now()
        campaigns = Campaign.objects.filter(
            status='active',
            target_type='new_users',
            auto_grant=True,
            start_date__lte=now,
            end_date__gte=now
        )

        for campaign in campaigns:
            if campaign.can_grant_more():
                # Verifica se o usuário é elegível
                eligible_users = CampaignService.get_eligible_users(campaign)
                if instance in eligible_users:
                    result = CampaignService.grant_premium(
                        instance,
                        campaign,
                        reason='Novo usuário - concessão automática'
                    )
                    if result['success']:
                        logger.info(f"Premium automático concedido para novo usuário: {instance.username}")
                    else:
                        logger.warning(f"Falha ao conceder Premium automático: {result.get('error')}")
    except Exception as e:
        logger.error(f"Erro ao verificar campanhas para novo usuário: {str(e)}")


@receiver(post_save, sender=CampaignGrant)
def campaign_grant_created(sender, instance, created, **kwargs):
    """
    Processa criação de nova concessão de campanha
    """
    if not created:
        return

    try:
        # Log da concessão
        logger.info(f"Nova concessão criada: {instance.campaign.name} → {instance.user.username}")

        # Aqui poderia ser adicionada lógica para enviar email de notificação
        # Por enquanto, apenas marca como pendente de notificação

    except Exception as e:
        logger.error(f"Erro ao processar nova concessão: {str(e)}")

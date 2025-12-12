"""
Tasks Celery para o módulo Finance
CGBookStore v3

Responsável por tarefas agendadas relacionadas a assinaturas Premium:
- Verificar assinaturas expirando (3 dias, 1 dia)
- Verificar assinaturas expiradas (enviar win-back)
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='finance.check_expiring_subscriptions')
def check_expiring_subscriptions():
    """
    Task que roda diariamente para verificar assinaturas que estão expirando.
    
    Envia emails de lembrete:
    - 3 dias antes da expiração
    - 1 dia antes da expiração
    - No dia da expiração (win-back)
    """
    from finance.models import Subscription
    from finance.email_service import PremiumEmailService
    
    now = timezone.now()
    results = {
        'expiring_3_days': 0,
        'expiring_1_day': 0,
        'expired_today': 0,
        'errors': 0,
    }
    
    logger.info("🔍 Iniciando verificação de assinaturas expirando...")
    
    # Assinaturas que expiram em exatamente 3 dias
    date_3_days = now.date() + timedelta(days=3)
    subscriptions_3days = Subscription.objects.filter(
        status='ativa',
        expiration_date__date=date_3_days
    ).select_related('user')
    
    for sub in subscriptions_3days:
        try:
            PremiumEmailService.send_expiring_reminder(
                user=sub.user,
                days_left=3,
                expires_at=sub.expiration_date
            )
            results['expiring_3_days'] += 1
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 3 dias para {sub.user.email}: {e}")
            results['errors'] += 1
    
    # Assinaturas que expiram amanhã (1 dia)
    date_1_day = now.date() + timedelta(days=1)
    subscriptions_1day = Subscription.objects.filter(
        status='ativa',
        expiration_date__date=date_1_day
    ).select_related('user')
    
    for sub in subscriptions_1day:
        try:
            PremiumEmailService.send_expiring_reminder(
                user=sub.user,
                days_left=1,
                expires_at=sub.expiration_date
            )
            results['expiring_1_day'] += 1
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 1 dia para {sub.user.email}: {e}")
            results['errors'] += 1
    
    # Assinaturas que expiraram hoje (win-back)
    subscriptions_expired = Subscription.objects.filter(
        status='ativa',
        expiration_date__date=now.date()
    ).select_related('user')
    
    for sub in subscriptions_expired:
        try:
            # Marcar como expirada
            sub.status = 'expirada'
            sub.save()
            
            # Enviar email de win-back
            PremiumEmailService.send_winback_email(
                user=sub.user,
                expired_at=sub.expiration_date
            )
            results['expired_today'] += 1
        except Exception as e:
            logger.error(f"Erro ao processar expiração para {sub.user.email}: {e}")
            results['errors'] += 1
    
    logger.info(
        f"✅ Verificação concluída: "
        f"{results['expiring_3_days']} emails (3 dias), "
        f"{results['expiring_1_day']} emails (1 dia), "
        f"{results['expired_today']} win-backs, "
        f"{results['errors']} erros"
    )
    
    return results


@shared_task(name='finance.send_test_retention_email')
def send_test_retention_email(user_id, email_type='expiring'):
    """
    Task para testar envio de emails de retenção.
    
    Args:
        user_id: ID do usuário
        email_type: 'expiring' ou 'winback'
    """
    from django.contrib.auth.models import User
    from finance.email_service import PremiumEmailService
    
    try:
        user = User.objects.get(id=user_id)
        
        if email_type == 'expiring':
            result = PremiumEmailService.send_expiring_reminder(
                user=user,
                days_left=3,
                expires_at=timezone.now() + timedelta(days=3)
            )
        else:
            result = PremiumEmailService.send_winback_email(
                user=user,
                expired_at=timezone.now()
            )
        
        return {'success': result, 'user': user.email, 'type': email_type}
        
    except User.DoesNotExist:
        return {'success': False, 'error': 'User not found'}

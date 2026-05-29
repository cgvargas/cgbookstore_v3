import logging
import threading
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_alert_now(activity_id: int = None, ai_alert_id: int = None) -> bool:
    """
    Executa o envio do alerta do WhatsApp imediatamente de forma síncrona.
    Retorna True em caso de sucesso ou se o alerta já tiver sido enviado, False caso contrário.
    """
    from .models import SuspiciousActivity, AIResponseAlert
    from .whatsapp_service import get_whatsapp_notifier

    notifier = get_whatsapp_notifier()

    try:
        if activity_id:
            try:
                activity = SuspiciousActivity.objects.get(pk=activity_id)
            except SuspiciousActivity.DoesNotExist:
                logger.error(f"SuspiciousActivity #{activity_id} não encontrada")
                return False

            if activity.alert_sent:
                logger.info(f"Alerta para SuspiciousActivity #{activity_id} já enviado. Ignorando.")
                return True

            success = notifier.send_suspicious_activity_alert(activity)
            if not success:
                logger.error(f"Falha ao enviar alerta de atividade suspeita #{activity_id}")
                return False

            logger.info(f"✅ Alerta de conduta suspeita #{activity_id} enviado via WhatsApp")
            return True

        elif ai_alert_id:
            try:
                alert = AIResponseAlert.objects.get(pk=ai_alert_id)
            except AIResponseAlert.DoesNotExist:
                logger.error(f"AIResponseAlert #{ai_alert_id} não encontrado")
                return False

            if alert.alert_sent:
                logger.info(f"Alerta para AIResponseAlert #{ai_alert_id} já enviado. Ignorando.")
                return True

            success = notifier.send_ai_error_alert(alert)
            if not success:
                logger.error(f"Falha ao enviar alerta de IA #{ai_alert_id}")
                return False

            logger.info(f"✅ Alerta de problema na IA #{ai_alert_id} enviado via WhatsApp")
            return True

        else:
            logger.warning("send_whatsapp_alert_now chamado sem activity_id ou ai_alert_id")
            return False

    except Exception as e:
        logger.error(f"Erro ao enviar alerta via WhatsApp (síncrono): {e}", exc_info=True)
        return False


def dispatch_whatsapp_alert(activity_id: int = None, ai_alert_id: int = None):
    """
    Despacha o alerta do WhatsApp de forma assíncrona.
    Se o Celery estiver configurado e FORCE_CELERY_ALERTS estiver ativado, usa Celery (.delay).
    Caso contrário, executa em uma Thread em background nativa do Python para não bloquear
    a requisição HTTP e evitar depender de um Celery worker em segundo plano no Render.
    """
    force_celery = getattr(settings, 'FORCE_CELERY_ALERTS', False)

    if force_celery:
        logger.info(f"Enfileirando alerta via Celery (activity_id={activity_id}, ai_alert_id={ai_alert_id})")
        send_whatsapp_alert_task.delay(activity_id=activity_id, ai_alert_id=ai_alert_id)
    else:
        logger.info(f"Disparando alerta em background thread nativa (activity_id={activity_id}, ai_alert_id={ai_alert_id})")
        def run_in_thread():
            from django.db import connection
            try:
                send_whatsapp_alert_now(activity_id=activity_id, ai_alert_id=ai_alert_id)
            except Exception as thread_err:
                logger.error(f"Erro na thread de envio de alerta WhatsApp: {thread_err}")
            finally:
                connection.close()  # Libera a conexão do banco de dados

        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()


@shared_task(
    name='monitoring.send_whatsapp_alert',
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60 segundos entre tentativas
    ignore_result=True,
)
def send_whatsapp_alert_task(self, activity_id: int = None, ai_alert_id: int = None):
    """
    Envia alerta WhatsApp de forma assíncrona usando Celery.
    """
    try:
        success = send_whatsapp_alert_now(activity_id=activity_id, ai_alert_id=ai_alert_id)
        if not success:
            raise Exception("Falha no envio do alerta")
    except Exception as exc:
        logger.error(f"❌ Erro ao enviar alerta WhatsApp (Celery): {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(
                f"❌ Máximo de tentativas atingido para alerta "
                f"(activity_id={activity_id}, ai_alert_id={ai_alert_id})"
            )


@shared_task(
    name='monitoring.send_daily_summary',
    ignore_result=True,
)
def send_daily_monitoring_summary():
    """
    Envia resumo diário de monitoramento via WhatsApp.

    Agendado via Celery Beat para rodar às 8h30 todos os dias.
    Compila estatísticas das últimas 24 horas e envia uma mensagem
    consolidada com o panorama de condutas suspeitas e erros da IA.
    """
    from .models import SuspiciousActivity, AIResponseAlert
    from .whatsapp_service import get_whatsapp_notifier
    from datetime import timedelta

    notifier = get_whatsapp_notifier()

    yesterday_start = timezone.now() - timedelta(hours=24)
    today_str = timezone.localtime(timezone.now()).strftime('%d/%m/%Y')

    try:
        # Estatísticas de atividades suspeitas (últimas 24h)
        suspicious_qs = SuspiciousActivity.objects.filter(created_at__gte=yesterday_start)
        suspicious_total = suspicious_qs.count()
        suspicious_critical = suspicious_qs.filter(severity='critical').count()
        suspicious_high = suspicious_qs.filter(severity='high').count()
        suspicious_unreviewed = suspicious_qs.filter(reviewed=False).count()

        # Estatísticas de alertas da IA (últimas 24h)
        ai_qs = AIResponseAlert.objects.filter(created_at__gte=yesterday_start)
        ai_total = ai_qs.count()
        ai_critical = ai_qs.filter(severity='critical').count()
        ai_unresolved = ai_qs.filter(resolved=False).count()

        stats = {
            'date': today_str,
            'suspicious_total': suspicious_total,
            'suspicious_critical': suspicious_critical,
            'suspicious_high': suspicious_high,
            'suspicious_unreviewed': suspicious_unreviewed,
            'ai_alerts_total': ai_total,
            'ai_alerts_critical': ai_critical,
            'ai_alerts_unresolved': ai_unresolved,
        }

        success = notifier.send_daily_summary(stats)

        if success:
            logger.info(f"✅ Resumo diário de monitoramento enviado — {today_str}")
        else:
            logger.error(f"❌ Falha ao enviar resumo diário de monitoramento — {today_str}")

    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo diário: {e}", exc_info=True)


@shared_task(
    name='monitoring.retry_pending_alerts',
    ignore_result=True,
)
def check_pending_alerts():
    """
    Re-tenta enviar alertas que não foram enviados ainda.

    Agendado para rodar a cada 15 minutos via Celery Beat.
    Busca registros onde alert_sent=False e tenta enviar novamente.
    Útil para recuperação de falhas de rede temporárias.
    """
    from .models import SuspiciousActivity, AIResponseAlert
    from datetime import timedelta

    # Só retentar alertas das últimas 6 horas
    cutoff = timezone.now() - timedelta(hours=6)

    # Alertas de atividade suspeita pendentes (alta e crítica)
    pending_activities = SuspiciousActivity.objects.filter(
        alert_sent=False,
        severity__in=['high', 'critical'],
        created_at__gte=cutoff,
    )

    for activity in pending_activities:
        logger.info(f"🔄 Re-tentando alerta para SuspiciousActivity #{activity.pk}")
        dispatch_whatsapp_alert(activity_id=activity.pk)

    # Alertas de IA pendentes (alta e crítica)
    pending_ai_alerts = AIResponseAlert.objects.filter(
        alert_sent=False,
        severity__in=['high', 'critical'],
        created_at__gte=cutoff,
    )

    for alert in pending_ai_alerts:
        logger.info(f"🔄 Re-tentando alerta para AIResponseAlert #{alert.pk}")
        dispatch_whatsapp_alert(ai_alert_id=alert.pk)

    total_pending = pending_activities.count() + pending_ai_alerts.count()
    if total_pending > 0:
        logger.info(f"🔄 {total_pending} alertas pendentes re-enfileirados")
    else:
        logger.debug("✅ Nenhum alerta pendente para re-tentar")

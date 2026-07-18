"""
Celery tasks do módulo Product Analytics.
"""
import datetime
import logging
from typing import Optional
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name="product_analytics.record_event",
    bind=True,
    ignore_result=True,
    max_retries=3,
    default_retry_delay=5,
)
def record_event_task(
    self,
    event_type: str,
    session_id: Optional[int],
    user_id: Optional[int],
    page_name: str,
    object_type: str,
    object_id: Optional[int],
    metadata: dict,
):
    """
    Task para registrar eventos de produto de forma assíncrona.
    """
    try:
        from .models import ProductEvent, AnalyticsSession

        session = None
        if session_id:
            try:
                session = AnalyticsSession.objects.get(pk=session_id)
            except AnalyticsSession.DoesNotExist:
                pass

        user = None
        if user_id:
            try:
                user = get_user_model().objects.get(pk=user_id)
            except Exception:
                pass

        ProductEvent.objects.create(
            session=session,
            user=user,
            event_type=event_type,
            page_name=page_name,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata or {},
        )
    except Exception as exc:
        logger.error(
            "[ProductAnalytics] record_event_task falhou: %s", exc, exc_info=True
        )
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(
                "[ProductAnalytics] Máximo de tentativas excedido para registrar evento %s",
                event_type,
            )


@shared_task(
    name="product_analytics.compute_daily_metrics",
    ignore_result=True,
)
def compute_daily_metrics_task():
    """
    Task diária para consolidar as métricas de ontem.
    Geralmente agendada para rodar às 3h AM.
    """
    try:
        from .services.snapshot_service import SnapshotService

        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        logger.info("[ProductAnalytics] Iniciando consolidacao automatica de ontem (%s)", yesterday)
        snapshots = SnapshotService.compute_day(yesterday)
        logger.info(
            "[ProductAnalytics] Consolidacao concluida. %d métricas salvas para %s.",
            len(snapshots),
            yesterday,
        )
    except Exception as exc:
        logger.error(
            "[ProductAnalytics] Falha na consolidacao automatica de ontem: %s",
            exc,
            exc_info=True,
        )


@shared_task(
    name="product_analytics.purge_expired_data",
    ignore_result=True,
)
def purge_expired_data_task():
    """
    Task diária para limpar eventos e sessões analíticas expiradas.
    Geralmente agendada para rodar às 4h AM.
    """
    try:
        from .utils import get_analytics_settings
        from .models import ProductEvent, AnalyticsSession

        cfg = get_analytics_settings()
        event_days = cfg.get("EVENT_RETENTION_DAYS", 90)
        session_days = cfg.get("SESSION_RETENTION_DAYS", 90)

        now = timezone.now()
        event_cutoff = now - timezone.timedelta(days=event_days)
        session_cutoff = now - timezone.timedelta(days=session_days)

        logger.info(
            "[ProductAnalytics] Iniciando expurgo (eventos > %d dias, sessoes > %d dias)...",
            event_days,
            session_days,
        )

        deleted_events, _ = ProductEvent.objects.filter(created_at__lt=event_cutoff).delete()
        deleted_sessions, _ = AnalyticsSession.objects.filter(last_activity_at__lt=session_cutoff).delete()

        logger.info(
            "[ProductAnalytics] Expurgo concluido. %d eventos e %d sessoes deletados.",
            deleted_events,
            deleted_sessions,
        )
    except Exception as exc:
        logger.error(
            "[ProductAnalytics] Falha no expurgo de dados expirados: %s",
            exc,
            exc_info=True,
        )

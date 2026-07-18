"""
SnapshotService — Consolida métricas diárias e snapshots analíticos.

Responsabilidade:
- Calcular as métricas oficiais para um dia específico.
- Gravar de forma idempotente usando DailyMetricSnapshot.upsert.
- Diferenciar dados completos de dados parciais (retroativos antes da implantação).
- Apoiar reconstrução histórica (backfill).
"""
import datetime
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import DailyMetricSnapshot, ProductEvent, AnalyticsSession
from ..constants import (
    METRIC_DAU,
    METRIC_WAU,
    METRIC_MAU,
    METRIC_DAU_MAU_RATIO,
    METRIC_RETENTION_D1,
    METRIC_RETENTION_D7,
    METRIC_RETENTION_D30,
    METRIC_NEW_USERS,
    METRIC_PREMIUM_CONVERSIONS,
    METRIC_SESSIONS_TOTAL,
    METRIC_PAGE_VIEWS_TOTAL,
    METRIC_SEARCHES_TOTAL,
    METRIC_PARTNER_CLICKS,
    METRIC_CHATBOT_SESSIONS,
    METRIC_BOOKS_ADDED,
    METRIC_BOOKS_COMPLETED,
    METRIC_AVG_SESSION_DURATION_SECONDS,
    METRIC_PAGES_PER_SESSION,
)
from .selectors import AppSelectors


class SnapshotService:
    """
    Serviço central para agregação e snapshots de métricas diárias.
    """

    @staticmethod
    def get_tracking_start_date() -> datetime.date:
        """
        Retorna a data do primeiro evento registrado.
        Se não houver eventos, retorna a data de hoje.
        """
        first_event = ProductEvent.objects.order_by("created_at").values("created_at").first()
        if first_event:
            return timezone.localtime(first_event["created_at"]).date()
        return timezone.localdate()

    @classmethod
    def compute_day(cls, target_date: datetime.date) -> list[DailyMetricSnapshot]:
        """
        Calcula e salva todas as métricas para a data especificada.
        Retorna uma lista dos snapshots salvos.
        """
        snapshots = []

        # Timestamps de início e fim do dia alvo
        day_start = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.min))
        day_end = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time.max))

        # Determina se a data é anterior ao início real do rastreamento de eventos
        tracking_start = cls.get_tracking_start_date()
        is_pre_tracking = target_date < tracking_start

        # ----------------------------------------------------------------------
        # 1. Métricas Canônicas (100% deriváveis de outros apps)
        # ----------------------------------------------------------------------
        # Estas são sempre completas (is_partial=False) porque os apps de origem possuem histórico completo

        # Novos usuários cadastrados
        new_users = AppSelectors.get_new_users_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_NEW_USERS,
            value=Decimal(new_users),
            source_apps=["auth"],
            is_partial=False
        ))

        # Livros adicionados à prateleira
        books_added = AppSelectors.get_books_added_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_BOOKS_ADDED,
            value=Decimal(books_added),
            source_apps=["accounts"],
            is_partial=False
        ))

        # Livros concluídos
        books_completed = AppSelectors.get_books_completed_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_BOOKS_COMPLETED,
            value=Decimal(books_completed),
            source_apps=["accounts"],
            is_partial=False
        ))

        # Conversões premium
        premium_conversions = AppSelectors.get_premium_conversions_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_PREMIUM_CONVERSIONS,
            value=Decimal(premium_conversions),
            source_apps=["finance"],
            is_partial=False
        ))

        # Cliques em parceiros
        partner_clicks = AppSelectors.get_partner_clicks_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_PARTNER_CLICKS,
            value=Decimal(partner_clicks),
            source_apps=["partners"],
            is_partial=False
        ))

        # Sessões de Chatbot
        chatbot_sessions = AppSelectors.get_chatbot_sessions_count(target_date)
        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_CHATBOT_SESSIONS,
            value=Decimal(chatbot_sessions),
            source_apps=["chatbot_literario"],
            is_partial=False
        ))

        # ----------------------------------------------------------------------
        # 2. Métricas Analíticas de Produto (baseadas em ProductEvent e AnalyticsSession)
        # ----------------------------------------------------------------------
        # Se for anterior ao rastreamento, são marcadas como is_partial=True e valor=0

        # DAU
        dau_value = 0
        if not is_pre_tracking:
            dau_value = ProductEvent.objects.filter(
                created_at__range=(day_start, day_end),
                user__isnull=False
            ).values("user").distinct().count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_DAU,
            value=Decimal(dau_value),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # WAU (Semana ISO contendo a data)
        wau_value = 0
        if not is_pre_tracking:
            week_start_date = target_date - datetime.timedelta(days=target_date.weekday())
            week_end_date = week_start_date + datetime.timedelta(days=6)
            week_start = timezone.make_aware(datetime.datetime.combine(week_start_date, datetime.time.min))
            week_end = timezone.make_aware(datetime.datetime.combine(week_end_date, datetime.time.max))

            wau_value = ProductEvent.objects.filter(
                created_at__range=(week_start, week_end),
                user__isnull=False
            ).values("user").distinct().count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_WAU,
            value=Decimal(wau_value),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # MAU (Mês calendário contendo a data)
        mau_value = 0
        if not is_pre_tracking:
            month_start_date = target_date.replace(day=1)
            # Próximo mês menos 1 dia
            if target_date.month == 12:
                next_month = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                next_month = target_date.replace(month=target_date.month + 1, day=1)
            month_end_date = next_month - datetime.timedelta(days=1)

            month_start = timezone.make_aware(datetime.datetime.combine(month_start_date, datetime.time.min))
            month_end = timezone.make_aware(datetime.datetime.combine(month_end_date, datetime.time.max))

            mau_value = ProductEvent.objects.filter(
                created_at__range=(month_start, month_end),
                user__isnull=False
            ).values("user").distinct().count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_MAU,
            value=Decimal(mau_value),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # DAU/MAU
        dau_mau_ratio = 0
        if mau_value > 0:
            dau_mau_ratio = (dau_value / mau_value) * 100

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_DAU_MAU_RATIO,
            value=Decimal(f"{dau_mau_ratio:.2f}"),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # Sessões Totais
        sessions_total = 0
        if not is_pre_tracking:
            sessions_total = AnalyticsSession.objects.filter(
                started_at__range=(day_start, day_end)
            ).count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_SESSIONS_TOTAL,
            value=Decimal(sessions_total),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # Page Views Totais
        page_views_total = 0
        if not is_pre_tracking:
            page_views_total = ProductEvent.objects.filter(
                created_at__range=(day_start, day_end),
                event_type="page_view"
            ).count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_PAGE_VIEWS_TOTAL,
            value=Decimal(page_views_total),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # Páginas por Sessão
        pages_per_session = 0
        if sessions_total > 0:
            pages_per_session = page_views_total / sessions_total

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_PAGES_PER_SESSION,
            value=Decimal(f"{pages_per_session:.2f}"),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # Buscas Totais
        searches_total = 0
        if not is_pre_tracking:
            searches_total = ProductEvent.objects.filter(
                created_at__range=(day_start, day_end),
                event_type="search_performed"
            ).count()

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_SEARCHES_TOTAL,
            value=Decimal(searches_total),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # Duração Média da Sessão (em segundos)
        avg_duration = 0
        if not is_pre_tracking and sessions_total > 0:
            # Seleciona sessões do dia que tenham last_activity_at ou ended_at
            sessions = AnalyticsSession.objects.filter(
                started_at__range=(day_start, day_end)
            )
            total_duration = 0
            count_valid = 0
            for s in sessions:
                dur = s.duration_seconds
                if dur is not None:
                    total_duration += dur
                    count_valid += 1
            if count_valid > 0:
                avg_duration = total_duration / count_valid

        snapshots.append(DailyMetricSnapshot.upsert(
            date=target_date,
            metric_name=METRIC_AVG_SESSION_DURATION_SECONDS,
            value=Decimal(f"{avg_duration:.1f}"),
            source_apps=["product_analytics"],
            is_partial=is_pre_tracking
        ))

        # ----------------------------------------------------------------------
        # 3. Retenção de Usuários (D1, D7, D30)
        # ----------------------------------------------------------------------
        # Retenção calcula quantos dos usuários cadastrados no target_date retornaram após X dias.

        for days_diff, metric_name in [
            (1, METRIC_RETENTION_D1),
            (7, METRIC_RETENTION_D7),
            (30, METRIC_RETENTION_D30),
        ]:
            retention_value = 0
            # Cohort: usuários registrados no target_date
            User = get_user_model()
            cohort_users = User.objects.filter(date_joined__range=(day_start, day_end)).values_list("pk", flat=True)
            cohort_size = len(cohort_users)

            if cohort_size > 0:
                # Intervalo de retorno baseado na definição aprovada
                if days_diff == 1:
                    # Exato D+1
                    ret_start = day_start + datetime.timedelta(days=1)
                    ret_end = day_end + datetime.timedelta(days=1)
                elif days_diff == 7:
                    # Qualquer dia entre D+2 e D+7
                    ret_start = day_start + datetime.timedelta(days=2)
                    ret_end = day_end + datetime.timedelta(days=7)
                else:
                    # Qualquer dia entre D+8 e D+30
                    ret_start = day_start + datetime.timedelta(days=8)
                    ret_end = day_end + datetime.timedelta(days=30)

                # Verifica se o fim da janela de retorno já passou (para não calcular retenção incompleta)
                if timezone.now() >= ret_start:
                    # Usuários que retornaram e geraram eventos de produto no intervalo
                    returned_count = ProductEvent.objects.filter(
                        user_id__in=cohort_users,
                        created_at__range=(ret_start, ret_end)
                    ).values("user").distinct().count()

                    retention_value = (returned_count / cohort_size) * 100
                else:
                    # Janela ainda não concluída
                    retention_value = 0

            snapshots.append(DailyMetricSnapshot.upsert(
                date=target_date,
                metric_name=metric_name,
                value=Decimal(f"{retention_value:.2f}"),
                source_apps=["auth", "product_analytics"],
                is_partial=is_pre_tracking or (timezone.now() < day_start + datetime.timedelta(days=days_diff))
            ))

        return snapshots

    @classmethod
    def backfill_range(cls, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Executa o cálculo de snapshots para um intervalo de datas (inclusive).
        Retorna o total de snapshots computados.
        """
        total = 0
        current = start_date
        while current <= end_date:
            snaps = cls.compute_day(current)
            total += len(snaps)
            current += datetime.timedelta(days=1)
        return total

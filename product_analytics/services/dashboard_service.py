"""
DashboardService — Fornece dados agregados e comparativos para o painel analítico.

Responsabilidade:
- Agregar os snapshots diários de um período (soma ou média conforme a métrica).
- Calcular o período comparativo anterior equivalente para gerar deltas percentuais.
- Estruturar séries temporais para geração de gráficos.
"""
import datetime
from decimal import Decimal
from django.db.models import Sum, Avg
from ..models import DailyMetricSnapshot
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


class DashboardService:
    """
    Serviço central de agregação analítica para visualização no dashboard.
    """

    # Define como agregar cada métrica sobre um intervalo de dias
    METRICS_AGGREGATION_TYPES = {
        METRIC_DAU: "avg",
        METRIC_WAU: "avg",
        METRIC_MAU: "avg",
        METRIC_DAU_MAU_RATIO: "avg",
        METRIC_RETENTION_D1: "avg",
        METRIC_RETENTION_D7: "avg",
        METRIC_RETENTION_D30: "avg",
        METRIC_NEW_USERS: "sum",
        METRIC_PREMIUM_CONVERSIONS: "sum",
        METRIC_SESSIONS_TOTAL: "sum",
        METRIC_PAGE_VIEWS_TOTAL: "sum",
        METRIC_SEARCHES_TOTAL: "sum",
        METRIC_PARTNER_CLICKS: "sum",
        METRIC_CHATBOT_SESSIONS: "sum",
        METRIC_BOOKS_ADDED: "sum",
        METRIC_BOOKS_COMPLETED: "sum",
        METRIC_AVG_SESSION_DURATION_SECONDS: "avg",
        METRIC_PAGES_PER_SESSION: "avg",
    }

    @classmethod
    def get_dashboard_metrics(
        cls,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> dict:
        """
        Gera o consolidado de todas as métricas para o período informado,
        junto com a comparação com o período anterior equivalente.
        """
        # 1. Calcula o período anterior equivalente
        days_diff = (end_date - start_date).days + 1
        comp_start_date = start_date - datetime.timedelta(days=days_diff)
        comp_end_date = end_date - datetime.timedelta(days=days_diff)

        # 2. Busca snapshots dos dois períodos
        current_snaps = DailyMetricSnapshot.objects.filter(date__range=(start_date, end_date))
        compare_snaps = DailyMetricSnapshot.objects.filter(date__range=(comp_start_date, comp_end_date))

        # 3. Agrega valores do período atual
        current_data = cls._aggregate_snapshots(current_snaps)
        compare_data = cls._aggregate_snapshots(compare_snaps)

        # 4. Consolida métricas com deltas
        metrics_summary = {}
        for metric, agg_type in cls.METRICS_AGGREGATION_TYPES.items():
            val_curr = current_data.get(metric, 0.0)
            val_comp = compare_data.get(metric, 0.0)

            # Calcula delta percentual
            if val_comp > 0:
                delta = ((val_curr - val_comp) / val_comp) * 100
            elif val_curr > 0:
                delta = 100.0
            else:
                delta = 0.0

            metrics_summary[metric] = {
                "value": round(val_curr, 2),
                "compare_value": round(val_comp, 2),
                "delta": round(delta, 1),
                "delta_abs": round(abs(delta), 1),
                "agg_type": agg_type,
            }

        # 5. Estrutura a série temporal para os gráficos do período atual
        # Agrupamento diário de métricas chave para gráfico
        time_series = {}
        date_list = []
        curr = start_date
        while curr <= end_date:
            date_list.append(curr.strftime("%d/%m"))
            curr += datetime.timedelta(days=1)

        # Inicializa listas vazias para séries temporais das principais métricas
        series_keys = [METRIC_DAU, METRIC_PAGE_VIEWS_TOTAL, METRIC_SESSIONS_TOTAL, METRIC_NEW_USERS]
        for key in series_keys:
            time_series[key] = [0.0] * len(date_list)

        # Popula as séries temporais
        for snap in current_snaps:
            if snap.metric_name in series_keys:
                snap_date_str = snap.date.strftime("%d/%m")
                if snap_date_str in date_list:
                    idx = date_list.index(snap_date_str)
                    time_series[snap.metric_name][idx] = float(snap.value)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "compare_start_date": comp_start_date,
            "compare_end_date": comp_end_date,
            "metrics": metrics_summary,
            "charts": {
                "labels": date_list,
                "series": time_series,
            }
        }

    @classmethod
    def _aggregate_snapshots(cls, queryset) -> dict:
        """
        Agrega um conjunto de snapshots aplicando soma ou média de acordo com o tipo da métrica.
        """
        # Agrega por soma
        sum_metrics = [k for k, v in cls.METRICS_AGGREGATION_TYPES.items() if v == "sum"]
        # Agrega por média
        avg_metrics = [k for k, v in cls.METRICS_AGGREGATION_TYPES.items() if v == "avg"]

        result = {}

        # Query de soma
        if sum_metrics:
            sums = (
                queryset
                .filter(metric_name__in=sum_metrics)
                .values("metric_name")
                .annotate(total=Sum("value"))
            )
            for item in sums:
                result[item["metric_name"]] = float(item["total"] or 0.0)

        # Query de média
        if avg_metrics:
            avgs = (
                queryset
                .filter(metric_name__in=avg_metrics)
                .values("metric_name")
                .annotate(average=Avg("value"))
            )
            for item in avgs:
                result[item["metric_name"]] = float(item["average"] or 0.0)

        return result

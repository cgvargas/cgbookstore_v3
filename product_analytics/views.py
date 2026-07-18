"""
Views do módulo Product Analytics.
"""
import datetime
import logging
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from .services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """
    Renderiza o painel analítico do produto.
    Apenas acessível para usuários do staff/administração.
    """
    today = timezone.localdate()

    # Período padrão: últimos 30 dias
    default_start = today - datetime.timedelta(days=30)
    default_end = today

    # Recupera parâmetros de filtro de data
    start_param = request.GET.get("start_date")
    end_param = request.GET.get("end_date")

    # Parsing das datas com fallback seguro
    try:
        if start_param:
            start_date = datetime.datetime.strptime(start_param, "%Y-%m-%d").date()
        else:
            start_date = default_start
    except ValueError:
        start_date = default_start

    try:
        if end_param:
            end_date = datetime.datetime.strptime(end_param, "%Y-%m-%d").date()
        else:
            end_date = default_end
    except ValueError:
        end_date = default_end

    # Garante ordem coerente das datas
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Obtém dados analíticos consolidados e comparativos
    data = DashboardService.get_dashboard_metrics(start_date, end_date)

    context = {
        "title": "Analytics de Produto",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "metrics": data["metrics"],
        "charts": data["charts"],
        "compare_start": data["compare_start_date"].strftime("%d/%m/%Y"),
        "compare_end": data["compare_end_date"].strftime("%d/%m/%Y"),
        # Atalhos rápidos de filtros de período
        "quick_filters": {
            "7d": {
                "start": (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d"),
            },
            "30d": {
                "start": (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d"),
            },
            "90d": {
                "start": (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d"),
            },
        }
    }

    return render(request, "product_analytics/dashboard.html", context)

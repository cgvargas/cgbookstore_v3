"""
Admin do módulo Product Analytics.

Interface administrativa para visualização de sessões e eventos.
Somente leitura (sem add/change/delete de eventos — dados são gerados pelo sistema).
"""
import logging
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone

from .models import AnalyticsSession, ProductEvent, DailyMetricSnapshot

logger = logging.getLogger(__name__)


# ==============================================================================
# HELPERS
# ==============================================================================

def _duration_display(session: AnalyticsSession) -> str:
    """Formata duração da sessão para exibição."""
    mins = session.duration_minutes
    if mins is None:
        return "—"
    if mins < 1:
        return "< 1 min"
    return f"{int(mins)} min"


# ==============================================================================
# ANALYTICS SESSION
# ==============================================================================

@admin.register(AnalyticsSession)
class AnalyticsSessionAdmin(admin.ModelAdmin):
    """
    Painel admin para visualização de sessões analíticas.
    Somente leitura — dados são gerados pelo middleware.
    """
    list_display = [
        "started_at_display",
        "user_display",
        "is_authenticated",
        "device_type",
        "browser_family",
        "entry_page",
        "exit_page",
        "duration_display",
        "source_display",
        "event_count_display",
    ]
    list_filter = [
        "is_authenticated",
        "device_type",
        "browser_family",
        "operating_system",
        ("started_at", admin.DateFieldListFilter),
    ]
    search_fields = [
        "user__username",
        "user__email",
        "session_key",
        "entry_page",
        "source",
        "referer_domain",
    ]
    readonly_fields = [
        "session_key",
        "user",
        "is_authenticated",
        "started_at",
        "last_activity_at",
        "ended_at",
        "entry_page",
        "exit_page",
        "referer_domain",
        "source",
        "medium",
        "campaign",
        "device_type",
        "browser_family",
        "operating_system",
        "created_at",
        "updated_at",
        "duration_display_detail",
    ]
    date_hierarchy = "started_at"
    ordering = ["-started_at"]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .annotate(event_count=Count("events"))
        )

    @admin.display(description="Início", ordering="started_at")
    def started_at_display(self, obj):
        local = timezone.localtime(obj.started_at)
        return format_html(
            '<span title="{}">{}</span>',
            local.strftime("%d/%m/%Y %H:%M:%S"),
            local.strftime("%d/%m %H:%M"),
        )

    @admin.display(description="Usuário", ordering="user__username")
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.pk,
                obj.user.username,
            )
        return format_html('<em style="color:#999;">Anônimo</em>')

    @admin.display(description="Duração")
    def duration_display(self, obj):
        return _duration_display(obj)

    @admin.display(description="Duração")
    def duration_display_detail(self, obj):
        return _duration_display(obj)

    @admin.display(description="Origem")
    def source_display(self, obj):
        if obj.source:
            return format_html(
                '<span title="medium={} campaign={}">{}</span>',
                obj.medium,
                obj.campaign,
                obj.source,
            )
        if obj.referer_domain:
            return format_html(
                '<em style="color:#666;">{}</em>', obj.referer_domain
            )
        return "direto"

    @admin.display(description="Eventos")
    def event_count_display(self, obj):
        count = getattr(obj, "event_count", 0)
        return count


# ==============================================================================
# PRODUCT EVENT
# ==============================================================================

@admin.register(ProductEvent)
class ProductEventAdmin(admin.ModelAdmin):
    """
    Painel admin para visualização de eventos de produto.
    Somente leitura — dados são gerados pelo sistema.
    """
    list_display = [
        "created_at_display",
        "event_type",
        "page_name",
        "object_info_display",
        "user_display",
        "session_display",
        "metadata_preview",
    ]
    list_filter = [
        "event_type",
        "page_name",
        ("created_at", admin.DateFieldListFilter),
    ]
    search_fields = [
        "user__username",
        "page_name",
        "event_type",
    ]
    readonly_fields = [
        "session",
        "user",
        "event_type",
        "page_name",
        "object_type",
        "object_id",
        "metadata",
        "created_at",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "session")

    @admin.display(description="Registrado em", ordering="created_at")
    def created_at_display(self, obj):
        local = timezone.localtime(obj.created_at)
        return format_html(
            '<span title="{}">{}</span>',
            local.strftime("%d/%m/%Y %H:%M:%S"),
            local.strftime("%d/%m %H:%M"),
        )

    @admin.display(description="Usuário")
    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return format_html('<em style="color:#999;">Anônimo</em>')

    @admin.display(description="Sessão")
    def session_display(self, obj):
        if obj.session:
            return format_html(
                '<a href="/admin/product_analytics/analyticssession/{}/change/">'
                "#{}</a>",
                obj.session.pk,
                obj.session.pk,
            )
        return "—"

    @admin.display(description="Objeto")
    def object_info_display(self, obj):
        if obj.object_type and obj.object_id:
            return format_html(
                '<span style="font-size:0.85em;">{} #{}</span>',
                obj.object_type,
                obj.object_id,
            )
        return "—"

    @admin.display(description="Metadata")
    def metadata_preview(self, obj):
        if obj.metadata:
            preview = str(obj.metadata)[:80]
            return format_html(
                '<code style="font-size:0.8em;">{}</code>', preview
            )
        return "—"


# ==============================================================================
# DAILY METRIC SNAPSHOT
# ==============================================================================

@admin.register(DailyMetricSnapshot)
class DailyMetricSnapshotAdmin(admin.ModelAdmin):
    """
    Painel admin para visualização de snapshots de métricas diárias.
    """
    list_display = [
        "date",
        "metric_name",
        "dimension_display",
        "value",
        "source_apps_display",
        "is_partial",
        "computed_at_display",
    ]
    list_filter = [
        "metric_name",
        "is_partial",
        ("date", admin.DateFieldListFilter),
    ]
    search_fields = ["metric_name", "dimension", "dimension_value"]
    readonly_fields = [
        "date",
        "metric_name",
        "dimension",
        "dimension_value",
        "value",
        "source_apps",
        "is_partial",
        "computed_at",
    ]
    date_hierarchy = "date"
    ordering = ["-date", "metric_name"]
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Dimensão")
    def dimension_display(self, obj):
        if obj.dimension:
            return format_html(
                '<span style="font-size:0.85em;">{} = {}</span>',
                obj.dimension,
                obj.dimension_value,
            )
        return format_html('<em style="color:#999;">total</em>')

    @admin.display(description="Apps")
    def source_apps_display(self, obj):
        if obj.source_apps:
            return ", ".join(obj.source_apps)
        return "—"

    @admin.display(description="⚠️ Parcial")
    def partial_display(self, obj):
        if obj.is_partial:
            return format_html(
                '<span style="color:#dc3545;font-weight:bold;" title="'
                'Dados incompletos para esta data">⚠️ Parcial</span>'
            )
        return format_html('<span style="color:green;">✅</span>')

    @admin.display(description="Computado em")
    def computed_at_display(self, obj):
        local = timezone.localtime(obj.computed_at)
        return local.strftime("%d/%m %H:%M")

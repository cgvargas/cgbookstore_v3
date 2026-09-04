# core/admin/image_rights_audit_log_admin.py
"""
Django Admin para Trilha Histórica de Auditoria de Direitos Autorais (ImageRightsAuditLog).
Interface append-only: somente leitura, sem edição nem exclusão.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from core.models.image_rights_audit_log import ImageRightsAuditLog


class ImageRightsAuditLogInline(admin.TabularInline):
    """
    Inline somente leitura incorporado no ImageRightsRecordAdmin.
    Exibe a linha do tempo cronológica decrescente dos eventos ocorridos sobre o ativo.
    """
    model = ImageRightsAuditLog
    extra = 0
    can_delete = False
    show_change_link = True
    classes = ['collapse']
    verbose_name = "📜 Evento de Auditoria"
    verbose_name_plural = "📜 Histórico de Auditoria e Governança do Ativo"
    fields = [
        'created_at_display',
        'event_badge',
        'performed_by',
        'source_badge',
        'description',
        'field_name',
        'old_value_display',
        'new_value_display',
        'takedown_link',
    ]
    readonly_fields = [
        'created_at_display',
        'event_badge',
        'performed_by',
        'source_badge',
        'description',
        'field_name',
        'old_value_display',
        'new_value_display',
        'takedown_link',
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def created_at_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
    created_at_display.short_description = "Data/Hora"

    def event_badge(self, obj):
        colors = {
            'record_created': '#27ae60',
            'record_updated': '#2980b9',
            'creator_changed': '#8e44ad',
            'rights_holder_changed': '#8e44ad',
            'licensor_changed': '#8e44ad',
            'source_changed': '#e67e22',
            'license_changed': '#d35400',
            'legal_basis_changed': '#16a085',
            'audit_status_changed': '#f39c12',
            'public_display_changed': '#c0392b',
            'permission_document_changed': '#20bf6b',
            'takedown_received': '#e74c3c',
            'takedown_status_changed': '#e67e22',
            'image_suspended': '#c0392b',
            'image_restored': '#27ae60',
            'takedown_resolved_keep': '#27ae60',
            'takedown_resolved_removed': '#c0392b',
            'integrity_divergence_detected': '#e74c3c',
            'checksum_updated': '#34495e',
        }
        color = colors.get(obj.event_type, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 7px; border-radius:8px; font-size:0.75rem; font-weight:600; white-space:nowrap;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_badge.short_description = "Tipo de Evento"

    def source_badge(self, obj):
        return format_html('<span style="color:#7f8c8d; font-size:0.75rem;">{}</span>', obj.get_source_display())
    source_badge.short_description = "Origem"

    def old_value_display(self, obj):
        if not obj.old_value:
            return "—"
        return format_html('<code style="color:#c0392b; font-size:0.75rem;">{}</code>', obj.old_value)
    old_value_display.short_description = "Valor Anterior"

    def new_value_display(self, obj):
        if not obj.new_value:
            return "—"
        return format_html('<code style="color:#27ae60; font-size:0.75rem;">{}</code>', obj.new_value)
    new_value_display.short_description = "Novo Valor"

    def takedown_link(self, obj):
        if not obj.takedown_request_id:
            return "—"
        url = reverse('admin:core_copyrighttakedownrequest_change', args=[obj.takedown_request_id])
        return format_html(
            '<a href="{}" style="color:#e74c3c; font-weight:600; text-decoration:underline;">⚠️ Contestação #{}</a>',
            url, obj.takedown_request_id
        )
    takedown_link.short_description = "Contestação"


@admin.register(ImageRightsAuditLog)
class ImageRightsAuditLogAdmin(admin.ModelAdmin):
    """
    Painel Central de Auditoria Histórica de Direitos Autorais e Governança Visual.
    Completamente append-only: apenas visualização permitida.
    """
    list_display = [
        'id',
        'created_at_display',
        'event_badge',
        'target_asset_link',
        'field_name_display',
        'safe_changes_display',
        'performed_by',
        'source_badge',
        'takedown_link',
    ]
    list_filter = [
        'event_type',
        'source',
        'created_at',
        'performed_by',
        'image_rights_record__content_type',
    ]
    search_fields = [
        'description',
        'field_name',
        'old_value',
        'new_value',
        'image_rights_record__work_title',
        'image_rights_record__creator_name',
        'image_rights_record__rights_holder_name',
        'image_rights_record__image_field_name',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at', '-id']

    # Bloqueio total contra inserção manual, alteração e exclusão via Django Admin
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Desabilitar exclusão em massa no Admin
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    fieldsets = (
        ('📜 Dados do Evento Histórico', {
            'fields': (
                ('event_type', 'created_at'),
                ('performed_by', 'source'),
                'description',
            )
        }),
        ('🎯 Ativo Visual Relacionado', {
            'fields': (
                'image_rights_record',
                'field_name',
                ('old_value', 'new_value'),
            )
        }),
        ('⚠️ Contestação e Contexto', {
            'fields': (
                'takedown_request',
                'metadata',
            )
        }),
    )
    readonly_fields = [
        'image_rights_record',
        'event_type',
        'created_at',
        'performed_by',
        'source',
        'field_name',
        'old_value',
        'new_value',
        'description',
        'takedown_request',
        'metadata',
    ]

    def created_at_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M:%S")
    created_at_display.short_description = "Data/Hora"
    created_at_display.admin_order_field = 'created_at'

    def event_badge(self, obj):
        colors = {
            'record_created': '#27ae60',
            'record_updated': '#2980b9',
            'creator_changed': '#8e44ad',
            'rights_holder_changed': '#8e44ad',
            'licensor_changed': '#8e44ad',
            'source_changed': '#e67e22',
            'license_changed': '#d35400',
            'legal_basis_changed': '#16a085',
            'audit_status_changed': '#f39c12',
            'public_display_changed': '#c0392b',
            'permission_document_changed': '#20bf6b',
            'takedown_received': '#e74c3c',
            'takedown_status_changed': '#e67e22',
            'image_suspended': '#c0392b',
            'image_restored': '#27ae60',
            'takedown_resolved_keep': '#27ae60',
            'takedown_resolved_removed': '#c0392b',
            'integrity_divergence_detected': '#e74c3c',
            'checksum_updated': '#34495e',
        }
        color = colors.get(obj.event_type, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_badge.short_description = "Tipo de Evento"
    event_badge.admin_order_field = 'event_type'

    def target_asset_link(self, obj):
        rec = obj.image_rights_record
        if not rec:
            return "—"
        url = reverse('admin:core_imagerightsrecord_change', args=[rec.pk])
        target_name = str(rec.content_object) if rec.content_object else f"ID #{rec.object_id}"
        model_name = rec.content_type.name if rec.content_type else "Objeto"
        return format_html(
            '<a href="{}" style="font-weight:600; text-decoration:underline;">{} &bull; {}</a><br><small style="color:#7f8c8d;">Campo: <code>{}</code></small>',
            url, model_name, target_name[:40], rec.image_field_name
        )
    target_asset_link.short_description = "Ativo Auditado"

    def field_name_display(self, obj):
        if not obj.field_name:
            return "—"
        return format_html('<code>{}</code>', obj.field_name)
    field_name_display.short_description = "Campo"

    def safe_changes_display(self, obj):
        if not obj.old_value and not obj.new_value:
            return format_html('<span style="color:#7f8c8d;">{}</span>', obj.description[:80])
        old_txt = obj.old_value or "(vazio)"
        new_txt = obj.new_value or "(vazio)"
        return format_html(
            '<div style="font-size:0.78rem;">'
            '<span style="color:#c0392b; text-decoration:line-through;">{}</span> &rarr; '
            '<strong style="color:#27ae60;">{}</strong>'
            '</div>',
            old_txt[:40], new_txt[:40]
        )
    safe_changes_display.short_description = "Alteração Registrada"

    def source_badge(self, obj):
        colors = {
            'admin': '#34495e',
            'service': '#2980b9',
            'command': '#8e44ad',
            'migration': '#d35400',
            'system': '#16a085',
        }
        color = colors.get(obj.source, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 6px; border-radius:6px; font-size:0.72rem;">{}</span>',
            color,
            obj.get_source_display()
        )
    source_badge.short_description = "Origem"
    source_badge.admin_order_field = 'source'

    def takedown_link(self, obj):
        if not obj.takedown_request_id:
            return "—"
        url = reverse('admin:core_copyrighttakedownrequest_change', args=[obj.takedown_request_id])
        return format_html(
            '<a href="{}" style="color:#e74c3c; font-weight:600; text-decoration:underline;">⚠️ #{}</a>',
            url, obj.takedown_request_id
        )
    takedown_link.short_description = "Contestação"

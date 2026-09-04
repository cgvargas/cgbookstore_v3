# core/admin/copyright_takedown_admin.py
"""
Django Admin para Gestão de Ocorrências de Contestação, Notificação e Takedown de Imagens.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from core.models.copyright_takedown import CopyrightTakedownRequest
from core.services.image_rights_service import ImageRightsAuditService
from core.services.image_rights_history_service import ImageRightsHistoryService


@admin.register(CopyrightTakedownRequest)
class CopyrightTakedownRequestAdmin(admin.ModelAdmin):
    """
    Administração de Notificações, Contestações e Procedimentos de Takedown de Ativos Visuais.
    """
    list_display = [
        'id_badge',
        'status_badge',
        'target_asset_link',
        'claimant_display',
        'claimant_role_display',
        'received_at',
        'public_display_status',
        'evidence_doc_link',
    ]
    list_filter = [
        'status',
        'claimant_role',
        'received_at',
        'resolved_at',
    ]
    search_fields = [
        'claimant_name',
        'claimant_email',
        'claimant_organization',
        'claim_description',
        'claimed_rights_basis',
        'image_rights_record__work_title',
        'image_rights_record__creator_name',
        'image_rights_record__credit_name',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'target_asset_details',
        'evidence_doc_preview',
    ]
    autocomplete_fields = ['image_rights_record']
    date_hierarchy = 'received_at'
    actions = [
        'action_mark_under_review',
        'action_suspend_preventively',
        'action_restore_public_display',
        'action_resolve_keep',
        'action_resolve_remove',
    ]

    def has_delete_permission(self, request, obj=None):
        """
        Governança: Contestações e ocorrências de takedown fazem parte do registro jurídico
        e administrativo da CG.BookStore e não podem ser excluídas normalmente.
        """
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    fieldsets = (
        ('Ativo Visual Contestado', {
            'fields': (
                'image_rights_record',
                'target_asset_details',
            )
        }),
        ('Estado da Ocorrência e Governança', {
            'fields': (
                'status',
                'received_at',
            )
        }),
        ('Identificação do Reclamante', {
            'fields': (
                'claimant_name',
                'claimant_email',
                'claimant_organization',
                'claimant_role',
            )
        }),
        ('Fundamentos e Documentação da Notificação', {
            'fields': (
                'claim_description',
                'claimed_rights_basis',
                'source_notice_url',
                'evidence_document',
                'evidence_doc_preview',
            )
        }),
        ('Tratamento Administrativo e Conclusão', {
            'fields': (
                'internal_notes',
                'resolution_notes',
                'resolved_at',
                'resolved_by',
                'created_by',
            )
        }),
        ('Metadados de Auditoria', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        old_status = None
        if not is_new:
            old_obj = CopyrightTakedownRequest.objects.filter(pk=obj.pk).first()
            if old_obj:
                old_status = old_obj.status

        if not change and not obj.created_by:
            obj.created_by = request.user

        # Se o status foi marcado como resolvido e não há resolved_at, preencher
        if obj.status in ['resolved_keep', 'resolved_removed', 'rejected'] and not obj.resolved_at:
            obj.resolved_at = timezone.now()
            if not obj.resolved_by:
                obj.resolved_by = request.user

        super().save_model(request, obj, form, change)

        # Trilha Histórica de Auditoria
        if is_new:
            ImageRightsHistoryService.log_takedown_received(
                takedown=obj,
                performed_by=request.user,
                source='admin'
            )
        elif old_status and old_status != obj.status:
            ImageRightsHistoryService.log_takedown_status_changed(
                takedown=obj,
                old_status=old_status,
                new_status=obj.status,
                performed_by=request.user,
                source='admin'
            )

        # Sincronização segura de governança com o ImageRightsRecord
        record = obj.image_rights_record
        if record:
            if obj.status == 'temporarily_suspended':
                record.public_display_allowed = False
                record.audit_status = 'restricted'
                record.save(update_fields=['public_display_allowed', 'audit_status'])
            elif obj.status == 'resolved_removed':
                record.public_display_allowed = False
                record.audit_status = 'restricted'
                record.save(update_fields=['public_display_allowed', 'audit_status'])
            elif obj.status == 'under_review' and record.audit_status not in ['contested', 'restricted']:
                record.audit_status = 'contested'
                record.save(update_fields=['audit_status'])

    # Métodos de Formatação Visual e Badges no Admin

    def id_badge(self, obj):
        return format_html('<span style="font-weight:700; color:#2c3e50;">#{}</span>', obj.pk)
    id_badge.short_description = "ID"
    id_badge.admin_order_field = 'id'

    def status_badge(self, obj):
        status_colors = {
            'received': ('#3498db', '📥 Recebida'),
            'under_review': ('#8e44ad', '🔍 Em análise'),
            'awaiting_information': ('#f39c12', '🟡 Aguardando info'),
            'temporarily_suspended': ('#c0392b', '⛔ Suspensa preventivamente'),
            'resolved_keep': ('#27ae60', '🟢 Resolvida (mantida)'),
            'resolved_removed': ('#d63031', '🔴 Resolvida (retirada)'),
            'rejected': ('#7f8c8d', '⚪ Rejeitada'),
        }
        color, label = status_colors.get(obj.status, ('#7f8c8d', obj.status))
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color, label
        )
    status_badge.short_description = "Status"
    status_badge.admin_order_field = 'status'

    def target_asset_link(self, obj):
        record = obj.image_rights_record
        if not record:
            return "-"
        url = reverse('admin:core_imagerightsrecord_change', args=[record.pk])
        target_name = str(record.content_object) if record.content_object else f"ID #{record.object_id}"
        model_name = record.content_type.name if record.content_type else "Objeto"
        return format_html(
            '<a href="{}" style="font-weight:600; text-decoration:underline;">{} &bull; {}</a><br><small style="color:#7f8c8d;">Campo: <code>{}</code></small>',
            url, model_name, target_name[:40], record.image_field_name
        )
    target_asset_link.short_description = "Ativo Contestado"

    def claimant_display(self, obj):
        name = obj.claimant_name or "Não informado"
        org = f" ({obj.claimant_organization})" if obj.claimant_organization else ""
        email = f"<br><small style='color:#7f8c8d;'>{obj.claimant_email}</small>" if obj.claimant_email else ""
        return format_html("<strong>{}</strong>{}{}", name, org, format_html(email))
    claimant_display.short_description = "Reclamante"

    def claimant_role_display(self, obj):
        return obj.get_claimant_role_display()
    claimant_role_display.short_description = "Papel Declarado"

    def public_display_status(self, obj):
        record = obj.image_rights_record
        if not record:
            return "-"
        if record.can_display_publicly:
            return format_html('<span style="color:{}; font-weight:600;">{}</span>', '#27ae60', '🟢 Visível')
        return format_html('<span style="color:{}; font-weight:600;">{}</span>', '#c0392b', '⛔ Bloqueada')
    public_display_status.short_description = "Exibição Pública"

    def evidence_doc_link(self, obj):
        if not obj.evidence_document:
            return format_html('<span style="color:{};">{}</span>', '#95a5a6', '—')
        url = reverse('core:protected_takedown_document_download', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" style="background:#34495e; color:#fff; padding:2px 7px; border-radius:4px; font-size:0.72rem; text-decoration:none;">📄 Ver Doc</a>',
            url
        )
    evidence_doc_link.short_description = "Doc Privado"

    def target_asset_details(self, obj):
        record = obj.image_rights_record
        if not record:
            return "Nenhum registro associado."
        url = reverse('admin:core_imagerightsrecord_change', args=[record.pk])
        model_name = record.content_type.name if record.content_type else "Objeto"
        target_name = str(record.content_object) if record.content_object else f"ID #{record.object_id}"
        return format_html(
            '<div style="background:#f8f9fa; padding:12px; border-radius:6px; border-left:4px solid #3498db;">'
            '<strong>Entidade:</strong> {} (#{}) — <em>{}</em><br>'
            '<strong>Campo de Imagem:</strong> <code>{}</code><br>'
            '<strong>Obra Visual / Título:</strong> {}<br>'
            '<strong>Autor / Criador Declarado:</strong> {}<br>'
            '<strong>Regime Jurídico / Licença:</strong> {}<br>'
            '<strong>Status de Auditoria Atual:</strong> {}<br>'
            '<strong>Checksum SHA-256:</strong> <code>{}</code><br>'
            '<a href="{}" class="button" style="margin-top:8px; display:inline-block;">Abrir ImageRightsRecord Completo</a>'
            '</div>',
            model_name, record.object_id, target_name,
            record.image_field_name,
            record.work_title or "Não informado",
            record.display_author or "Não informado",
            record.get_license_type_display() if record.license_type else "Não informado",
            record.get_audit_status_display(),
            record.image_checksum or "Não calculado",
            url
        )
    target_asset_details.short_description = "Detalhes do Ativo Contestado"

    def evidence_doc_preview(self, obj):
        if not obj.evidence_document:
            return "Nenhum arquivo ou documento comprobatório anexado."
        url = reverse('core:protected_takedown_document_download', args=[obj.pk])
        return format_html(
            '<div style="background:#f8f9fa; padding:10px; border-radius:6px; border:1px solid #e2e8f0;">'
            '🔒 <strong>Documento Comprobatório Privado</strong>: <code>{}</code><br>'
            '<a href="{}" target="_blank" class="button" style="margin-top:6px; display:inline-block;">Baixar / Visualizar Documento Seguro</a>'
            '</div>',
            obj.evidence_document.name,
            url
        )
    evidence_doc_preview.short_description = "Visualização do Documento"

    # Actions Administrativas Seguras e Auditáveis

    @admin.action(description="🔍 Marcar selecionadas como 'Em análise' (audit_status -> contestada)")
    def action_mark_under_review(self, request, queryset):
        count = 0
        for takedown in queryset:
            takedown.status = 'under_review'
            takedown.save(update_fields=['status', 'updated_at'])
            record = takedown.image_rights_record
            if record and record.audit_status not in ['contested', 'restricted']:
                record.audit_status = 'contested'
                record.save(update_fields=['audit_status'])
            count += 1
        self.message_user(request, f"{count} contestação(ões) marcada(s) como 'Em análise'. Ativos marcados como contestados.", messages.SUCCESS)

    @admin.action(description="⛔ Suspender imagem preventivamente (bloqueia exibição pública)")
    def action_suspend_preventively(self, request, queryset):
        count = 0
        for takedown in queryset:
            takedown.status = 'temporarily_suspended'
            takedown.save(update_fields=['status', 'updated_at'])
            record = takedown.image_rights_record
            if record:
                ImageRightsAuditService.suspend_image_asset(
                    record,
                    request_user=request.user,
                    notes=f"Suspensão via contestação #{takedown.pk}",
                    takedown_request=takedown,
                    source='admin'
                )
            count += 1
        self.message_user(request, f"{count} ativo(s) suspenso(s) preventivamente da exibição pública com preservação total de evidências.", messages.WARNING)

    @admin.action(description="🟢 Restaurar exibição pública da imagem")
    def action_restore_public_display(self, request, queryset):
        success_count = 0
        failed_msgs = []
        for takedown in queryset:
            record = takedown.image_rights_record
            if record:
                success, msg = ImageRightsAuditService.restore_image_asset(
                    record,
                    request_user=request.user,
                    takedown_request=takedown,
                    source='admin'
                )
                if success:
                    success_count += 1
                else:
                    failed_msgs.append(f"#{takedown.pk}: {msg}")
        if success_count:
            self.message_user(request, f"Exibição pública restaurada para {success_count} ativo(s).", messages.SUCCESS)
        if failed_msgs:
            self.message_user(request, f"Atenção: Não foi possível restaurar {len(failed_msgs)} ativo(s): " + " | ".join(failed_msgs), messages.ERROR)

    @admin.action(description="🟢 Resolver ocorrência MANTENDO a imagem (uso legítimo confirmado)")
    def action_resolve_keep(self, request, queryset):
        count = 0
        notes = []
        for takedown in queryset:
            _success, msg = ImageRightsAuditService.resolve_takedown_atomic(
                takedown, resolution_type='keep', request_user=request.user
            )
            count += 1
            if "permanece SUSPENSO" in msg:
                notes.append(f"Contestação #{takedown.pk}: mantida, mas ativo continua suspenso por haver outra contestação pendente.")
        self.message_user(request, f"{count} contestação(ões) resolvida(s) mantendo o uso da imagem.", messages.SUCCESS)
        if notes:
            self.message_user(request, " ".join(notes), messages.WARNING)

    @admin.action(description="🔴 Resolver ocorrência RETIRANDO a imagem (bloqueio definitivo preservando registro)")
    def action_resolve_remove(self, request, queryset):
        count = 0
        for takedown in queryset:
            ImageRightsAuditService.resolve_takedown_atomic(
                takedown, resolution_type='remove', request_user=request.user
            )
            count += 1
        self.message_user(request, f"{count} ocorrência(s) resolvida(s) com RETIRADA DA IMAGEM. Exibição pública bloqueada e histórico/evidências preservados.", messages.WARNING)

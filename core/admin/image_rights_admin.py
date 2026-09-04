# core/admin/image_rights_admin.py
"""
Django Admin para ImageRightsRecord.
Contém formulários com dropdown dinâmico de campos de imagem reais,
inlines genéricos, validações assistidas não-bloqueantes e badges visuais.
"""

from django import forms
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.models.image_rights import ImageRightsRecord
from core.models.copyright_takedown import CopyrightTakedownRequest
from core.admin.image_rights_audit_log_admin import ImageRightsAuditLogInline
from core.services.image_rights_history_service import ImageRightsHistoryService


class CopyrightTakedownRequestInline(admin.StackedInline):
    """
    Inline de Contestações e Notificações de Takedown diretamente dentro do ImageRightsRecord.
    """
    model = CopyrightTakedownRequest
    extra = 0
    classes = ['collapse']
    verbose_name = "⚠️ Ocorrência de Contestação / Takedown"
    verbose_name_plural = "⚠️ Ocorrências de Contestação / Takedown Vinculadas"
    fields = [
        ('status', 'received_at'),
        ('claimant_name', 'claimant_email', 'claimant_organization', 'claimant_role'),
        'claim_description',
        'claimed_rights_basis',
        'source_notice_url',
        'evidence_document',
        'internal_notes',
        'resolution_notes',
        ('resolved_at', 'resolved_by'),
    ]
    readonly_fields = ['created_at', 'updated_at']


class ImageRightsRecordForm(forms.ModelForm):
    """
    Formulário do ImageRightsRecord.
    Valida dinamicamente se o image_field_name selecionado/informado
    corresponde a um campo real de imagem no modelo.
    """
    class Meta:
        model = ImageRightsRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se temos uma instância de modelo ou content_type pré-definido, gerar escolhas dinâmicas
        ct_id = None
        if self.instance and self.instance.content_type_id:
            ct_id = self.instance.content_type_id
        elif 'content_type' in self.initial:
            ct_id = self.initial['content_type']
            
        if ct_id:
            try:
                ct = ContentType.objects.get(pk=ct_id)
                model_cls = ct.model_class()
                if model_cls:
                    image_fields = []
                    for f in model_cls._meta.get_fields():
                        if isinstance(f, (models.ImageField, models.FileField)):
                            image_fields.append((f.name, f"{f.verbose_name} ({f.name})"))
                    if image_fields:
                        self.fields['image_field_name'] = forms.ChoiceField(
                            choices=image_fields,
                            label="Campo da Imagem",
                            help_text="Selecione qual imagem do modelo está sendo auditada."
                        )
            except Exception:
                pass

    def clean(self):
        cleaned_data = super().clean()
        ct = cleaned_data.get('content_type')
        field_name = cleaned_data.get('image_field_name')

        if ct and field_name:
            model_cls = ct.model_class()
            if model_cls:
                valid_field = False
                for f in model_cls._meta.get_fields():
                    if f.name == field_name and isinstance(f, (models.ImageField, models.FileField)):
                        valid_field = True
                        break
                if not valid_field:
                    raise forms.ValidationError(
                        f"O campo '{field_name}' não é um campo de imagem válido no modelo {model_cls._meta.verbose_name}."
                    )

        return cleaned_data


class ImageRightsRecordInline(GenericStackedInline):
    """
    Inline Genérico para exibir a gestão de procedência e licença
    diretamente nos formulários dos modelos que contêm imagens.
    """
    model = ImageRightsRecord
    form = ImageRightsRecordForm
    extra = 0
    classes = ['collapse']
    verbose_name = "🛡️ Registro de Direitos Autorais de Imagem"
    verbose_name_plural = "🛡️ Direitos Autorais e Procedência das Imagens"
    fields = [
        'image_field_name',
        'audit_status',
        'work_title',
        ('creator_name', 'rights_holder_name'),
        ('licensor_name', 'credit_name'),
        ('source_url', 'license_type'),
        ('license_url', 'legal_basis'),
        ('usage_purpose', 'is_ai_generated'),
        'display_dimensions',
        'permission_document',
        'usage_notes',
    ]

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        return super().get_extra(request, obj, **kwargs)


@admin.register(ImageRightsRecord)
class ImageRightsRecordAdmin(admin.ModelAdmin):
    """
    Admin central para auditoria direta de ImageRightsRecord.
    """
    form = ImageRightsRecordForm
    inlines = [CopyrightTakedownRequestInline, ImageRightsAuditLogInline]
    list_display = [
        'id',
        'content_type',
        'object_id',
        'image_field_name',
        'audit_status_badge',
        'provenance_badge',
        'public_display_badge',
        'disputes_count_badge',
        'purpose_badge',
        'legal_basis_badge',
        'license_badge',
        'display_dimensions',
        'creator_or_credit_display',
        'is_ai_badge',
        'has_doc_badge',
        'created_at',
    ]
    list_filter = [
        'audit_status',
        'provenance_provider',
        'is_auto_imported',
        'public_display_allowed',
        'usage_purpose',
        'legal_basis',
        'license_type',
        'is_ai_generated',
        'content_type',
        'created_at',
    ]
    search_fields = [
        'creator_name',
        'rights_holder_name',
        'licensor_name',
        'credit_name',
        'work_title',
        'source_url',
        'provenance_provider',
        'provider_asset_id',
        'usage_notes',
        'image_field_name',
        'display_dimensions',
    ]
    readonly_fields = ['created_at', 'updated_at', 'image_checksum', 'image_width_px', 'image_height_px', 'file_size_kb', 'provenance_imported_at']
    actions = [
        'action_suspend_public_display',
        'action_restore_public_display',
    ]

    def has_delete_permission(self, request, obj=None):
        """
        Governança: Impede a exclusão administrativa de registros que possuam
        histórico de auditoria ou contestações vinculadas.
        """
        if obj:
            if obj.audit_logs.exists() or obj.takedown_requests.exists():
                return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    fieldsets = (
        ('📌 Vínculo do Ativo Visual', {
            'fields': ('content_type', 'object_id', 'image_field_name', 'image_file_name', 'image_checksum')
        }),
        ('🛡️ Auditoria, Conformidade e Governança', {
            'description': (
                'A presença de uma imagem em site de editora, Amazon, Google Books, Open Library, '
                'Wikimedia, rede social ou outro serviço não constitui, isoladamente, licença ou autorização de uso. '
                'Registre a fonte em "Fonte Original da Imagem" e documente separadamente a licença, autorização ou fundamento jurídico aplicável.'
            ),
            'fields': (
                'audit_status',
                'public_display_allowed',
            )
        }),
        ('🔗 Procedência Técnica e Rastreabilidade Externa', {
            'description': (
                '⚠️ AVISO DE GOVERNANÇA: A procedência técnica identifica de onde o arquivo ou referência '
                'foi obtido. Ela NÃO representa, por si só, licença, autorização, titularidade ou regularização jurídica.'
            ),
            'fields': (
                ('provenance_provider', 'is_auto_imported'),
                ('provenance_method', 'provider_asset_id'),
                'provenance_imported_at',
                'provenance_metadata',
            )
        }),
        ('🎨 Autoria, Criação e Titularidade dos Direitos', {
            'description': 'Identifique separadamente o criador da obra visual, o titular dos direitos patrimoniais e a entidade licenciante.',
            'fields': (
                'work_title',
                'creator_name',
                'rights_holder_name',
                'licensor_name',
                'credit_name',
                'is_ai_generated',
            )
        }),
        ('📄 Procedência, Licenciamento e Fundamento Jurídico', {
            'description': 'A indicação da fonte representa apenas a origem técnica do arquivo e não presume autorização de uso.',
            'fields': (
                'source_url',
                'license_type',
                'license_url',
                'legal_basis',
                'usage_purpose',
                'permission_document',
                'usage_notes',
            )
        }),
        ('📐 Dimensões e Resolução Técnica', {
            'fields': ('display_dimensions', ('image_width_px', 'image_height_px', 'file_size_kb'))
        }),
        ('🕒 Auditoria e Responsabilidade', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def provenance_badge(self, obj):
        if not obj.provenance_provider:
            if obj.is_ai_generated:
                return mark_safe('<span style="background:#6c5ce7; color:#fff; padding:2px 7px; border-radius:8px; font-size:0.75rem;">🤖 IA Interna</span>')
            return mark_safe('<span style="color:#7f8c8d; font-size:0.75rem;">—</span>')
        
        provider_styles = {
            'google_books': ('#4285F4', '🔍 Google Books'),
            'open_library': ('#e67e22', '📖 Open Library'),
            'project_gutenberg': ('#8e44ad', '📜 Project Gutenberg'),
            'unsplash': ('#000000', '📷 Unsplash'),
            'wikimedia': ('#2c3e50', '🏛️ Wikimedia'),
            'amazon': ('#f39c12', '🛒 Amazon'),
            'publisher': ('#d35400', '📚 Editora'),
        }
        color, label = provider_styles.get(obj.provenance_provider, ('#34495e', f'🌐 {obj.provenance_provider}'))
        auto_tag = ' ⚡' if obj.is_auto_imported else ''
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 7px; border-radius:8px; font-size:0.73rem; font-weight:600;">{}{}</span>',
            color, label, auto_tag
        )
    provenance_badge.short_description = "Procedência Técnica"
    provenance_badge.admin_order_field = 'provenance_provider'

    def public_display_badge(self, obj):
        if obj.can_display_publicly:
            return format_html('<span style="color:{}; font-weight:600;">{}</span>', '#27ae60', '🟢 Permitida')
        return format_html('<span style="color:{}; font-weight:600;">{}</span>', '#c0392b', '⛔ Bloqueada')
    public_display_badge.short_description = "Exibição Pública"

    def disputes_count_badge(self, obj):
        active_count = obj.takedown_requests.filter(
            status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
        ).count()
        total_count = obj.takedown_requests.count()
        if active_count > 0:
            return format_html('<span style="background:#c0392b; color:#fff; padding:2px 7px; border-radius:10px; font-size:0.72rem; font-weight:700;">⚠️ {} ativa(s)</span>', active_count)
        elif total_count > 0:
            return format_html('<span style="color:#7f8c8d; font-size:0.75rem;">{} hist.</span>', total_count)
        return "—"
    disputes_count_badge.short_description = "Contestações"

    @admin.action(description="⛔ Suspender exibição pública (public_display_allowed=False, audit_status='restricted')")
    def action_suspend_public_display(self, request, queryset):
        count = 0
        for record in queryset:
            ImageRightsAuditService.suspend_image_asset(record, request_user=request.user)
            count += 1
        self.message_user(request, f"{count} ativo(s) suspenso(s) preventivamente da exibição pública.", messages.WARNING)

    @admin.action(description="🟢 Restaurar exibição pública (public_display_allowed=True)")
    def action_restore_public_display(self, request, queryset):
        success_count = 0
        failed_msgs = []
        for record in queryset:
            success, msg = ImageRightsAuditService.restore_image_asset(record, request_user=request.user)
            if success:
                success_count += 1
            else:
                failed_msgs.append(f"Ativo #{record.pk}: {msg}")
        if success_count:
            self.message_user(request, f"Exibição pública restaurada para {success_count} ativo(s).", messages.SUCCESS)
        if failed_msgs:
            self.message_user(request, f"Atenção: Não foi possível restaurar {len(failed_msgs)} ativo(s): " + " | ".join(failed_msgs), messages.ERROR)

    def audit_status_badge(self, obj):
        colors = {
            'not_audited': '#7f8c8d',
            'under_review': '#2980b9',
            'regularized': '#27ae60',
            'pending': '#f39c12',
            'contested': '#c0392b',
            'restricted': '#d63031',
        }
        color = colors.get(obj.audit_status, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color,
            obj.get_audit_status_display()
        )
    audit_status_badge.short_description = "Status Auditoria"

    def creator_or_credit_display(self, obj):
        if obj.creator_name:
            return format_html('<span style="font-weight:600;">{}</span>', obj.creator_name)
        elif obj.credit_name:
            return format_html('<span style="color:#7f8c8d; font-style:italic;">{} (legado)</span>', obj.credit_name)
        return "—"
    creator_or_credit_display.short_description = "Criador / Crédito"

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        old_instance = None
        if not is_new:
            old_instance = ImageRightsRecord.objects.filter(pk=obj.pk).first()

        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        # Trilha Histórica de Auditoria
        if is_new:
            ImageRightsHistoryService.log_record_created(
                record=obj,
                performed_by=request.user,
                source='admin'
            )
        elif old_instance:
            ImageRightsHistoryService.log_record_changes(
                record=obj,
                old_instance=old_instance,
                performed_by=request.user,
                source='admin'
            )

        # Validações não-bloqueantes com mensagens orientadoras para o administrador
        if obj.audit_status == 'regularized' and not obj.license_type and not obj.legal_basis:
            messages.warning(
                request,
                f"⚠️ Atenção: O registro [{obj.image_field_name}] foi marcado como 'Regularizada', mas não possui regime de licença ou fundamento jurídico registrado."
            )
        elif obj.audit_status == 'contested':
            messages.error(
                request,
                f"🔴 Registro Contestada: O ativo visual [{obj.image_field_name}] foi marcado sob contestação ou disputa jurídica."
            )
        elif not obj.license_type and not obj.legal_basis:
            messages.warning(
                request,
                f"⚠️ Aviso: O registro de imagem [{obj.image_field_name}] foi salvo sem regime de licença ou enquadramento jurídico definido."
            )
        elif obj.license_type == 'cc' and not obj.license_url:
            messages.warning(
                request,
                f"⚠️ Aviso Creative Commons: A imagem [{obj.image_field_name}] está marcada como Creative Commons mas não possui a 'URL Oficial da Licença' cadastrada."
            )
        
        author_name = obj.creator_name or obj.credit_name
        if author_name and not obj.source_url:
            messages.info(
                request,
                f"💡 Recomendação: O criador/crédito '{author_name}' foi informado. Se possível, cadastre também a URL da fonte original."
            )

        if obj.license_type in ['licensed', 'other'] and not obj.permission_document and not obj.usage_notes:
            messages.warning(
                request,
                f"⚠️ Pendência Documental: Para imagens com licença '{obj.get_license_type_display()}', é recomendável anexar o documento de autorização ou registrar observações internas."
            )

    # Badges visuais para a listagem
    def purpose_badge(self, obj):
        if not obj.usage_purpose:
            return "—"
        colors = {
            'review_debate': '#8e44ad',
            'affiliate_promotion': '#f39c12',
            'author_bio': '#2980b9',
            'event_publicity': '#e67e22',
            'adaptation_info': '#16a085',
            'institutional': '#27ae60',
        }
        color = colors.get(obj.usage_purpose, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color,
            obj.get_usage_purpose_display()
        )
    purpose_badge.short_description = "Finalidade"

    def legal_basis_badge(self, obj):
        if not obj.legal_basis:
            return "—"
        colors = {
            'fair_use_art46': '#27ae60',
            'express_consent': '#2980b9',
            'amazon_affiliate_terms': '#f39c12',
            'public_domain': '#16a085',
            'creative_commons': '#8e44ad',
            'own_production': '#34495e',
        }
        color = colors.get(obj.legal_basis, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color,
            obj.get_legal_basis_display()
        )
    legal_basis_badge.short_description = "Fundamento Legal"

    def license_badge(self, obj):
        if not obj.license_type:
            return format_html('<span style="background:#e74c3c; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>', '⚠️ Sem Licença')
        colors = {
            'own': '#27ae60',
            'licensed': '#2980b9',
            'cc': '#8e44ad',
            'public_domain': '#16a085',
            'publisher': '#d35400',
            'amazon': '#f39c12',
            'google_books': '#4285F4',
        }
        color = colors.get(obj.license_type, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{}</span>',
            color,
            obj.get_license_type_display()
        )
    license_badge.short_description = "Licença"

    def is_ai_badge(self, obj):
        if obj.is_ai_generated:
            return format_html('<span style="background:#6c5ce7; color:#fff; padding:2px 6px; border-radius:8px; font-size:0.75rem;">{}</span>', '🤖 IA')
        return "—"
    is_ai_badge.short_description = "Origem IA"

    def has_doc_badge(self, obj):
        if obj.permission_document:
            return format_html('<span style="background:#20bf6b; color:#fff; padding:2px 6px; border-radius:8px; font-size:0.75rem;">{}</span>', '📜 Com Doc')
        return "—"
    has_doc_badge.short_description = "Documento"


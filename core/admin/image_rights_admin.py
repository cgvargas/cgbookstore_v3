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

from core.models.image_rights import ImageRightsRecord


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
        ('work_title', 'credit_name'),
        ('license_type', 'is_ai_generated'),
        ('source_url', 'license_url'),
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
    list_display = [
        'id',
        'content_type',
        'object_id',
        'image_field_name',
        'license_badge',
        'credit_name',
        'is_ai_badge',
        'has_doc_badge',
        'created_at',
    ]
    list_filter = [
        'license_type',
        'is_ai_generated',
        'content_type',
        'created_at',
    ]
    search_fields = [
        'credit_name',
        'work_title',
        'source_url',
        'usage_notes',
        'image_field_name',
    ]
    readonly_fields = ['created_at', 'updated_at', 'image_checksum']

    fieldsets = (
        ('📌 Vínculo do Ativo Visual', {
            'fields': ('content_type', 'object_id', 'image_field_name', 'image_file_name', 'image_checksum')
        }),
        ('🎨 Atribuição e Fonte (TASL)', {
            'fields': ('work_title', 'credit_name', 'source_url', 'is_ai_generated')
        }),
        ('⚖️ Licença e Governança Jurídica', {
            'fields': ('license_type', 'license_url', 'permission_document', 'usage_notes')
        }),
        ('🕒 Auditoria e Responsabilidade', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        # Validações não-bloqueantes com mensagens orientadoras para o administrador
        if not obj.license_type:
            messages.warning(
                request,
                f"⚠️ Aviso: O registro de imagem [{obj.image_field_name}] foi salvo sem regime de licença definido. Ele permanecerá pendente na auditoria."
            )
        elif obj.license_type == 'cc' and not obj.license_url:
            messages.warning(
                request,
                f"⚠️ Aviso Creative Commons: A imagem [{obj.image_field_name}] está marcada como Creative Commons mas não possui a 'URL Oficial da Licença' cadastrada."
            )
        
        if obj.credit_name and not obj.source_url:
            messages.info(
                request,
                f"💡 Recomendação: O crédito '{obj.credit_name}' foi informado. Se possível, cadastre também a URL da fonte original."
            )

        if obj.license_type in ['licensed', 'other'] and not obj.permission_document and not obj.usage_notes:
            messages.warning(
                request,
                f"⚠️ Pendência Documental: Para imagens com licença '{obj.get_license_type_display()}', é recomendável anexar o documento de autorização ou registrar observações internas."
            )

    # Badges visuais para a listagem
    def license_badge(self, obj):
        if not obj.license_type:
            return format_html('<span style="background:#e74c3c; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⚠️ Sem Licença</span>')
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
            f'<span style="background:{color}; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">{obj.get_license_type_display()}</span>'
        )
    license_badge.short_description = "Licença"

    def is_ai_badge(self, obj):
        if obj.is_ai_generated:
            return format_html('<span style="background:#6c5ce7; color:#fff; padding:2px 6px; border-radius:8px; font-size:0.75rem;">🤖 IA</span>')
        return "—"
    is_ai_badge.short_description = "Origem IA"

    def has_doc_badge(self, obj):
        if obj.permission_document:
            return format_html('<span style="background:#20bf6b; color:#fff; padding:2px 6px; border-radius:8px; font-size:0.75rem;">📜 Com Doc</span>')
        return "—"
    has_doc_badge.short_description = "Documento"

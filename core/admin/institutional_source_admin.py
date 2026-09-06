# core/admin/institutional_source_admin.py
"""
Interface administrativa para o modelo InstitutionalSource (Fase 3A.1).
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models.institutional_source import InstitutionalSource


@admin.register(InstitutionalSource)
class InstitutionalSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'domain_link',
        'institution_type',
        'terms_link',
        'is_verified',
        'is_active',
        'terms_retrieved_at',
    ]
    list_filter = [
        'institution_type',
        'is_verified',
        'is_active',
        'created_at',
    ]
    search_fields = ['name', 'domain', 'main_url', 'notes']
    readonly_fields = [
        'created_at',
        'updated_at',
        'verified_at',
        'terms_retrieved_at',
        'terms_content_hash',
    ]

    fieldsets = [
        ('Identificação Institucional', {
            'fields': [
                'name',
                'domain',
                'institution_type',
                'main_url',
                'is_active',
            ]
        }),
        ('Páginas Oficiais de Termos e Direitos', {
            'fields': [
                'terms_url',
                'permissions_url',
                'terms_summary',
                'terms_content_hash',
                'terms_retrieved_at',
            ]
        }),
        ('Validação e Curadoria', {
            'fields': [
                'is_verified',
                'verified_at',
                'verified_by',
                'notes',
                'created_at',
                'updated_at',
            ]
        }),
    ]

    def domain_link(self, obj):
        if obj.main_url:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">🌐 {}</a>', obj.main_url, obj.domain)
        return obj.domain
    domain_link.short_description = "Domínio"

    def terms_link(self, obj):
        if obj.terms_url:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">📜 Termos</a>', obj.terms_url)
        return format_html('<span style="color: #999;">Não informado</span>')
    terms_link.short_description = "Termos de Uso"

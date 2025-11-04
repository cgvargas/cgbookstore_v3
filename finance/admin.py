from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.http import HttpResponse
import json
from .models import Subscription, Product, Order, OrderItem, TransactionLog, Campaign, CampaignGrant
from .services import CampaignService

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'price', 'payment_method', 'expiration_date', 'is_active_display']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'mp_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'mp_subscription_id', 'mp_payment_id']
    
    def is_active_display(self, obj):
        if obj.is_active():
            return format_html('<span style="color: green;">Ativa</span>')
        return format_html('<span style="color: red;">Inativa</span>')
    is_active_display.short_description = 'Ativa?'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'product_type', 'price', 'stock', 'is_active']
    list_filter = ['product_type', 'is_active', 'created_at']
    search_fields = ['name', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'mp_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at', 'mp_payment_id']
    inlines = [OrderItemInline]

@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'user', 'amount', 'mp_status', 'created_at']
    list_filter = ['transaction_type', 'mp_status', 'created_at']
    search_fields = ['user__username', 'mp_payment_id']
    readonly_fields = ['created_at', 'raw_data']


class CampaignGrantInline(admin.TabularInline):
    model = CampaignGrant
    extra = 0
    readonly_fields = ['user', 'granted_at', 'expires_at', 'is_active', 'was_notified']
    can_delete = False
    verbose_name = 'Concessão Recente'
    verbose_name_plural = 'Concessões Recentes (últimas 10)'

    # Limita a 10 registros
    def get_max_num(self, request, obj=None, **kwargs):
        """Limita a 10 concessões"""
        return 10

    def get_queryset(self, request):
        """Otimiza queryset sem fazer slice (evita erro de filter após slice)"""
        qs = super().get_queryset(request)
        # Apenas otimiza com select_related e ordena, SEM fazer slice aqui
        return qs.select_related('user', 'subscription').order_by('-granted_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'target_type', 'duration_days', 'status_display',
        'start_date', 'end_date', 'total_granted_display', 'total_eligible', 'remaining_display',
        'execution_count_display', 'last_execution_display'
    ]
    list_filter = ['status', 'target_type', 'duration_days', 'start_date', 'auto_grant', 'execution_count']
    search_fields = ['name', 'description']
    readonly_fields = ['total_granted', 'total_eligible', 'created_at', 'updated_at', 'created_by',
                       'execution_count', 'last_execution_date']
    inlines = [CampaignGrantInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'status')
        }),
        ('Configuração', {
            'fields': ('duration_days', 'target_type', 'criteria', 'auto_grant', 'send_notification', 'max_grants')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Estatísticas', {
            'fields': ('total_granted', 'total_eligible'),
            'classes': ('collapse',)
        }),
        ('Controle de Execuções', {
            'fields': ('execution_count', 'last_execution_date'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = [
        'execute_campaign',
        'preview_eligible_users',
        'activate_campaigns',
        'pause_campaigns',
        'complete_campaigns'
    ]

    def status_display(self, obj):
        colors = {
            'draft': 'gray',
            'active': 'green',
            'paused': 'orange',
            'completed': 'blue',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def total_granted_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{}</span>',
            obj.total_granted
        )
    total_granted_display.short_description = 'Concedidos'

    def remaining_display(self, obj):
        remaining = obj.get_remaining_grants()
        if remaining == float('inf'):
            return format_html('<span style="color: blue;">Ilimitado</span>')
        return format_html(
            '<span style="color: orange; font-weight: bold;">{}</span>',
            int(remaining)
        )
    remaining_display.short_description = 'Restantes'

    def execution_count_display(self, obj):
        """Exibe número de execuções com badge visual"""
        if obj.execution_count == 0:
            return format_html(
                '<span style="background-color: #666666; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">Nunca executada</span>'
            )
        elif obj.execution_count == 1:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">✓ 1 vez</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #2196F3; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">✓ {} vezes</span>',
                obj.execution_count
            )
    execution_count_display.short_description = 'Execuções'

    def last_execution_display(self, obj):
        """Exibe última execução com formatação condicional"""
        if not obj.last_execution_date:
            return format_html('<span style="color: #999; font-style: italic;">Nunca</span>')

        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.last_execution_date

        # Formatação da data
        date_str = obj.last_execution_date.strftime('%d/%m/%Y %H:%M')

        # Cor baseada em quão recente foi a execução
        if diff.days == 0:
            color = '#4CAF50'  # Verde - hoje
            time_ago = 'Hoje'
        elif diff.days <= 7:
            color = '#2196F3'  # Azul - última semana
            time_ago = f'Há {diff.days} dia(s)'
        elif diff.days <= 30:
            color = '#FF9800'  # Laranja - último mês
            time_ago = f'Há {diff.days} dias'
        else:
            color = '#999999'  # Cinza - mais de 30 dias
            time_ago = f'Há {diff.days} dias'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span><br>'
            '<span style="color: #666; font-size: 10px;">{}</span>',
            color, date_str, time_ago
        )
    last_execution_display.short_description = 'Última Execução'

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def execute_campaign(self, request, queryset):
        """Action para executar campanhas selecionadas"""
        executed = 0
        total_granted = 0
        errors = []

        for campaign in queryset:
            if not campaign.is_active_now():
                errors.append(f"{campaign.name}: Campanha não está ativa no período")
                continue

            result = CampaignService.execute_campaign(campaign, preview=False)
            if result['success']:
                executed += 1
                total_granted += result.get('granted_count', 0)
            else:
                errors.append(f"{campaign.name}: {result.get('error')}")

        if executed > 0:
            self.message_user(
                request,
                f"{executed} campanha(s) executada(s). Total de {total_granted} Premiums concedidos.",
                messages.SUCCESS
            )
        if errors:
            self.message_user(
                request,
                f"Erros: {'; '.join(errors)}",
                messages.WARNING
            )
    execute_campaign.short_description = "Executar campanhas selecionadas"

    def preview_eligible_users(self, request, queryset):
        """Action para pré-visualizar usuários elegíveis"""
        if queryset.count() > 1:
            self.message_user(
                request,
                "Selecione apenas uma campanha por vez para pré-visualização",
                messages.ERROR
            )
            return

        campaign = queryset.first()
        result = CampaignService.execute_campaign(campaign, preview=True)

        if result['success']:
            eligible_users = result.get('eligible_users', [])
            usernames = [u['username'] for u in eligible_users[:10]]

            msg = f"Campanha '{campaign.name}': {result['eligible_count']} usuários elegíveis"
            if eligible_users:
                msg += f". Primeiros 10: {', '.join(usernames)}"

            self.message_user(request, msg, messages.INFO)
        else:
            self.message_user(
                request,
                f"Erro ao buscar elegíveis: {result.get('error')}",
                messages.ERROR
            )
    preview_eligible_users.short_description = "Pré-visualizar usuários elegíveis"

    def activate_campaigns(self, request, queryset):
        """Ativa campanhas selecionadas"""
        updated = queryset.update(status='active')
        self.message_user(
            request,
            f"{updated} campanha(s) ativada(s)",
            messages.SUCCESS
        )
    activate_campaigns.short_description = "Ativar campanhas"

    def pause_campaigns(self, request, queryset):
        """Pausa campanhas selecionadas"""
        updated = queryset.update(status='paused')
        self.message_user(
            request,
            f"{updated} campanha(s) pausada(s)",
            messages.SUCCESS
        )
    pause_campaigns.short_description = "Pausar campanhas"

    def complete_campaigns(self, request, queryset):
        """Marca campanhas como concluídas"""
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            f"{updated} campanha(s) marcada(s) como concluída(s)",
            messages.SUCCESS
        )
    complete_campaigns.short_description = "Marcar como concluídas"


@admin.register(CampaignGrant)
class CampaignGrantAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'campaign', 'granted_at', 'expires_at',
        'is_active_display', 'was_notified'
    ]
    list_filter = ['campaign', 'is_active', 'was_notified', 'granted_at']
    search_fields = [
        'user__username', 'user__email',
        'campaign__name', 'reason'
    ]
    readonly_fields = ['granted_at', 'revoked_at', 'expires_at']
    date_hierarchy = 'granted_at'

    fieldsets = (
        ('Informações', {
            'fields': ('campaign', 'user', 'subscription')
        }),
        ('Datas', {
            'fields': ('granted_at', 'expires_at', 'revoked_at')
        }),
        ('Status', {
            'fields': ('is_active', 'was_notified', 'reason')
        })
    )

    def is_active_display(self, obj):
        if obj.is_active and not obj.is_expired():
            return format_html('<span style="color: green;">✓ Ativo</span>')
        elif obj.is_expired():
            return format_html('<span style="color: orange;">⏰ Expirado</span>')
        else:
            return format_html('<span style="color: red;">✗ Revogado</span>')
    is_active_display.short_description = 'Status'

    actions = ['revoke_grants']

    def revoke_grants(self, request, queryset):
        """Revoga concessões selecionadas"""
        revoked = 0
        for grant in queryset.filter(is_active=True):
            result = CampaignService.revoke_premium(grant)
            if result['success']:
                revoked += 1

        self.message_user(
            request,
            f"{revoked} concessão(ões) revogada(s)",
            messages.SUCCESS
        )
    revoke_grants.short_description = "Revogar concessões selecionadas"

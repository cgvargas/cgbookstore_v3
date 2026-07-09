from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from .models import AffiliatePartner, AffiliatePartnerClick


@admin.register(AffiliatePartner)
class AffiliatePartnerAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'slug',
        'tracking_id',
        'url_base',
        'ativo',
        'prioridade',
        'updated_at'
    )
    list_filter = (
        'ativo',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'nome',
        'slug',
        'tracking_id'
    )
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-prioridade', 'nome')
    actions = ['make_active', 'make_inactive']

    @admin.action(description="Ativar parceiros selecionados")
    def make_active(self, request, queryset):
        rows_updated = queryset.update(ativo=True)
        if rows_updated == 1:
            message_bit = "1 parceiro comercial foi"
        else:
            message_bit = f"{rows_updated} parceiros comerciais foram"
        self.message_user(request, f"{message_bit} marcado(s) como ativo(s) com sucesso.")

    @admin.action(description="Desativar parceiros selecionados")
    def make_inactive(self, request, queryset):
        rows_updated = queryset.update(ativo=False)
        if rows_updated == 1:
            message_bit = "1 parceiro comercial foi"
        else:
            message_bit = f"{rows_updated} parceiros comerciais foram"
        self.message_user(request, f"{message_bit} marcado(s) como inativo(s) com sucesso.")


@admin.register(AffiliatePartnerClick)
class AffiliatePartnerClickAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'partner',
        'book',
        'user',
        'device',
        'browser',
        'os',
        'ip_address'
    )
    list_filter = (
        'partner',
        'device',
        'browser',
        'os',
        'created_at',
        'book__category'
    )
    search_fields = (
        'book__title',
        'book__author__name',
        'partner__nome',
        'user__username',
        'device',
        'browser',
        'os',
        'ip_address'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at', 'user', 'session_key', 'book', 'partner', 
        'destination_url', 'ip_address', 'user_agent', 
        'browser', 'os', 'device', 'referer', 'language'
    )

    def has_add_permission(self, request):
        """Impedir a criação manual de logs de cliques pelo admin."""
        return False

    def changelist_view(self, request, extra_context=None):
        """
        Sobrescreve a listagem do admin para injetar agregados estatísticos dinâmicos
        para os gráficos (respeitando os filtros aplicados na tela).
        """
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Só injeta os gráficos caso a listagem esteja renderizando normalmente
        if hasattr(response, 'context_data'):
            cl = response.context_data['cl']
            queryset = cl.get_queryset(request)
            
            # 1. Cliques por dia (últimos 30 dias com cliques)
            clicks_by_day = list(reversed(
                queryset.annotate(day=TruncDay('created_at'))
                .values('day')
                .annotate(count=Count('id'))
                .order_by('-day')[:30]
            ))
            
            # 2. Cliques por mês (últimos 12 meses)
            clicks_by_month = list(reversed(
                queryset.annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('-month')[:12]
            ))
            
            # 3. Cliques por parceiro
            clicks_by_partner = (
                queryset.values('partner__nome')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # 4. Cliques por categoria literária
            clicks_by_category = (
                queryset.values('book__category__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # 5. Cliques por autor
            clicks_by_author = (
                queryset.values('book__author__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # 6. Cliques por livro (Top 10)
            clicks_by_book = (
                queryset.values('book__title')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # 7. Cliques por dispositivo
            clicks_by_device = (
                queryset.values('device')
                .annotate(count=Count('id'))
                .order_by('-count')
            )

            # Estruturar dados para Chart.js
            chart_data = {
                'by_day': {
                    'labels': [c['day'].strftime('%d/%m') if c['day'] else '' for c in clicks_by_day],
                    'values': [c['count'] for c in clicks_by_day]
                },
                'by_month': {
                    'labels': [c['month'].strftime('%m/%Y') if c['month'] else '' for c in clicks_by_month],
                    'values': [c['count'] for c in clicks_by_month]
                },
                'by_partner': {
                    'labels': [c['partner__nome'] or 'Direto/Sem Parceiro' for c in clicks_by_partner],
                    'values': [c['count'] for c in clicks_by_partner]
                },
                'by_category': {
                    'labels': [c['book__category__name'] or 'Sem Categoria' for c in clicks_by_category],
                    'values': [c['count'] for c in clicks_by_category]
                },
                'by_author': {
                    'labels': [c['book__author__name'] or 'Sem Autor' for c in clicks_by_author],
                    'values': [c['count'] for c in clicks_by_author]
                },
                'by_book': {
                    'labels': [c['book__title'][:25] + '...' if c['book__title'] and len(c['book__title']) > 25 else (c['book__title'] or 'Sem Título') for c in clicks_by_book],
                    'values': [c['count'] for c in clicks_by_book]
                },
                'by_device': {
                    'labels': [c['device'] or 'Desconhecido' for c in clicks_by_device],
                    'values': [c['count'] for c in clicks_by_device]
                }
            }

            # Resumo Estatístico para os cards de KPI
            total_clicks = queryset.count()
            unique_visitors = queryset.values('session_key', 'user').distinct().count()
            
            mobile_clicks = queryset.filter(device='Mobile').count()
            mobile_pct = round((mobile_clicks / total_clicks * 100), 1) if total_clicks > 0 else 0
            
            stats_summary = {
                'total_clicks': total_clicks,
                'unique_visitors': unique_visitors,
                'mobile_pct': mobile_pct,
            }

            extra_context = extra_context or {}
            extra_context['chart_data'] = chart_data
            extra_context['stats_summary'] = stats_summary
            
            response.context_data.update(extra_context)
            
        return response

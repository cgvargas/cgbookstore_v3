"""
Admin personalizado para AccountDeletion com estatísticas e análises.
"""
from django.contrib import admin
from django.db.models import Count, Q, Avg
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from accounts.models import AccountDeletion


@admin.register(AccountDeletion)
class AccountDeletionAdmin(admin.ModelAdmin):
    """
    Admin avançado para exclusões de conta com:
    - Dashboard de estatísticas
    - Filtros múltiplos
    - Busca avançada
    - Análise de churn
    - Exportação de dados
    """

    # ===== LISTAGEM =====
    list_display = [
        'username_display',
        'email_display',
        'deleted_at_display',
        'reason_display',
        'premium_badge',
        'books_badge',
        'membership_badge',
        'email_status_badge',
    ]

    list_filter = [
        'deletion_reason',
        'was_premium',
        'email_sent',
        ('deleted_at', admin.DateFieldListFilter),
    ]

    search_fields = [
        'username',
        'email',
        'user_id',
        'other_reason',
    ]

    readonly_fields = [
        'username',
        'email',
        'user_id',
        'deleted_at',
        'user_created_at',
        'deletion_reason',
        'other_reason',
        'was_premium',
        'books_count',
        'days_as_member',
        'email_sent',
        'email_error',
        'email_sent_at',
        'ip_address',
        'user_agent',
        'deletion_summary',
    ]

    fieldsets = (
        ('📋 Informações do Usuário', {
            'fields': (
                'username',
                'email',
                'user_id',
            )
        }),
        ('📅 Datas', {
            'fields': (
                'deleted_at',
                'user_created_at',
                'days_as_member',
            )
        }),
        ('💬 Motivo da Exclusão', {
            'fields': (
                'deletion_reason',
                'other_reason',
            )
        }),
        ('📊 Estatísticas do Usuário', {
            'fields': (
                'was_premium',
                'books_count',
            )
        }),
        ('📧 Status do Email', {
            'fields': (
                'email_sent',
                'email_sent_at',
                'email_error',
            )
        }),
        ('🔍 Informações Técnicas', {
            'fields': (
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',)
        }),
        ('📝 Notas Administrativas', {
            'fields': (
                'admin_notes',
            )
        }),
        ('📑 Resumo', {
            'fields': (
                'deletion_summary',
            )
        }),
    )

    # Permitir edição apenas de admin_notes
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editando
            readonly = list(self.readonly_fields)
            readonly.remove('admin_notes')
            return readonly
        return self.readonly_fields

    # ===== EXIBIÇÕES PERSONALIZADAS =====

    @admin.display(description='Usuário', ordering='username')
    def username_display(self, obj):
        return format_html(
            '<strong style="color: #333;">{}</strong><br>'
            '<small style="color: #666;">ID: {}</small>',
            obj.username,
            obj.user_id
        )

    @admin.display(description='Email')
    def email_display(self, obj):
        return format_html(
            '<a href="mailto:{}" style="color: #0066cc;">{}</a>',
            obj.email,
            obj.email
        )

    @admin.display(description='Data de Exclusão', ordering='deleted_at')
    def deleted_at_display(self, obj):
        now = timezone.now()
        delta = now - obj.deleted_at

        if delta.days == 0:
            time_ago = "Hoje"
        elif delta.days == 1:
            time_ago = "Ontem"
        elif delta.days < 7:
            time_ago = f"{delta.days} dias atrás"
        elif delta.days < 30:
            weeks = delta.days // 7
            time_ago = f"{weeks} semana{'s' if weeks > 1 else ''} atrás"
        else:
            months = delta.days // 30
            time_ago = f"{months} mês{'es' if months > 1 else ''} atrás"

        return format_html(
            '<span style="color: #333;">{}</span><br>'
            '<small style="color: #999;">{}</small>',
            obj.deleted_at.strftime('%d/%m/%Y %H:%M'),
            time_ago
        )

    @admin.display(description='Motivo')
    def reason_display(self, obj):
        reason_colors = {
            'nao_uso_mais': '#f39c12',
            'falta_funcionalidades': '#e74c3c',
            'dificuldade_uso': '#e67e22',
            'problemas_tecnicos': '#c0392b',
            'preco_premium': '#8e44ad',
            'privacidade': '#2980b9',
            'migrando_plataforma': '#16a085',
            'conta_duplicada': '#27ae60',
            'outros': '#95a5a6',
            'nao_informado': '#7f8c8d',
        }

        color = reason_colors.get(obj.deletion_reason, '#333')
        reason_text = obj.deletion_reason_display

        return format_html(
            '<span style="display: inline-block; background: {}; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">'
            '{}</span>',
            color,
            reason_text[:50]
        )

    @admin.display(description='Premium')
    def premium_badge(self, obj):
        if obj.was_premium:
            return format_html(
                '<span style="background: #f39c12; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">👑 PREMIUM</span>'
            )
        return format_html(
            '<span style="color: #999; font-size: 11px;">Free</span>'
        )

    @admin.display(description='Livros')
    def books_badge(self, obj):
        if obj.books_count > 100:
            color = '#e74c3c'
            icon = '📚📚📚'
        elif obj.books_count > 50:
            color = '#e67e22'
            icon = '📚📚'
        elif obj.books_count > 10:
            color = '#f39c12'
            icon = '📚'
        elif obj.books_count > 0:
            color = '#95a5a6'
            icon = '📖'
        else:
            return format_html('<span style="color: #ccc;">0</span>')

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.books_count
        )

    @admin.display(description='Tempo')
    def membership_badge(self, obj):
        if not obj.days_as_member:
            return format_html('<span style="color: #999;">N/A</span>')

        if obj.days_as_member < 7:
            color = '#e74c3c'
            icon = '🆕'
        elif obj.days_as_member < 30:
            color = '#e67e22'
            icon = '📅'
        elif obj.days_as_member < 365:
            color = '#f39c12'
            icon = '📆'
        else:
            color = '#27ae60'
            icon = '⭐'

        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            icon,
            obj.membership_duration_display
        )

    @admin.display(description='Email')
    def email_status_badge(self, obj):
        if obj.email_sent:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ Enviado</span>'
            )
        elif obj.email_error:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;" title="{}">✗ Erro</span>',
                obj.email_error[:100]
            )
        else:
            return format_html(
                '<span style="background: #95a5a6; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">○ Não enviado</span>'
            )

    @admin.display(description='Resumo Completo')
    def deletion_summary(self, obj):
        """Exibe um resumo visual completo da exclusão."""
        html = f'''
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="margin-top: 0; color: #333;">📊 Resumo da Exclusão</h3>

            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">👤 Usuário:</td>
                    <td style="padding: 10px;">{obj.username} (ID: {obj.user_id})</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">📧 Email:</td>
                    <td style="padding: 10px;">{obj.email}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">🗓️ Excluído em:</td>
                    <td style="padding: 10px;">{obj.deleted_at.strftime('%d/%m/%Y às %H:%M')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">⏱️ Tempo como membro:</td>
                    <td style="padding: 10px;">{obj.membership_duration_display} ({obj.days_as_member or 0} dias)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">💬 Motivo:</td>
                    <td style="padding: 10px; color: #e74c3c; font-weight: bold;">{obj.deletion_reason_display}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">👑 Status:</td>
                    <td style="padding: 10px;">{'<span style="color: #f39c12; font-weight: bold;">PREMIUM</span>' if obj.was_premium else 'Free'}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">📚 Livros:</td>
                    <td style="padding: 10px;">{obj.books_count} livros na biblioteca</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px; font-weight: bold;">✉️ Email:</td>
                    <td style="padding: 10px;">{obj.email_status_display}</td>
                </tr>
                {f'<tr style="border-bottom: 1px solid #ddd;"><td style="padding: 10px; font-weight: bold;">🌐 IP:</td><td style="padding: 10px;">{obj.ip_address}</td></tr>' if obj.ip_address else ''}
            </table>
        </div>
        '''
        return mark_safe(html)

    # ===== ACTIONS PERSONALIZADAS =====

    @admin.action(description='📊 Exportar selecionados (CSV)')
    def export_csv(self, request, queryset):
        """Exporta exclusões selecionadas para CSV."""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="exclusoes_conta.csv"'
        response.write('\ufeff')  # BOM para Excel reconhecer UTF-8

        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'ID', 'Data Exclusão', 'Motivo',
            'Motivo Detalhado', 'Era Premium', 'Livros', 'Dias Membro',
            'Email Enviado', 'Erro Email', 'IP'
        ])

        for obj in queryset:
            writer.writerow([
                obj.username,
                obj.email,
                obj.user_id,
                obj.deleted_at.strftime('%d/%m/%Y %H:%M'),
                obj.get_deletion_reason_display(),
                obj.other_reason or '',
                'Sim' if obj.was_premium else 'Não',
                obj.books_count,
                obj.days_as_member or 0,
                'Sim' if obj.email_sent else 'Não',
                obj.email_error or '',
                obj.ip_address or '',
            ])

        return response

    actions = [export_csv]

    # ===== DASHBOARD CUSTOMIZADO =====

    def get_urls(self):
        """Adiciona URL customizada para dashboard."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'dashboard/',
                self.admin_site.admin_view(self.dashboard_view),
                name='account_deletion_dashboard'
            ),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """View customizada com dashboard de estatísticas."""
        # Período de análise
        today = timezone.now()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)

        # Estatísticas gerais
        total_deletions = AccountDeletion.objects.count()
        deletions_30d = AccountDeletion.objects.filter(deleted_at__gte=last_30_days).count()
        deletions_7d = AccountDeletion.objects.filter(deleted_at__gte=last_7_days).count()

        # Por motivo
        by_reason = AccountDeletion.objects.values('deletion_reason').annotate(
            count=Count('id')
        ).order_by('-count')

        # Premium vs Free
        premium_count = AccountDeletion.objects.filter(was_premium=True).count()
        free_count = total_deletions - premium_count

        # Email
        email_sent_count = AccountDeletion.objects.filter(email_sent=True).count()
        email_failed_count = AccountDeletion.objects.filter(
            email_sent=False,
            email_error__isnull=False
        ).count()

        # Média de tempo como membro
        avg_days = AccountDeletion.objects.aggregate(
            avg=Avg('days_as_member')
        )['avg'] or 0

        # Média de livros
        avg_books = AccountDeletion.objects.aggregate(
            avg=Avg('books_count')
        )['avg'] or 0

        # Exclusões recentes
        recent_deletions = AccountDeletion.objects.all()[:10]

        context = {
            **self.admin_site.each_context(request),
            'title': 'Dashboard de Exclusões de Conta',
            'total_deletions': total_deletions,
            'deletions_30d': deletions_30d,
            'deletions_7d': deletions_7d,
            'by_reason': by_reason,
            'premium_count': premium_count,
            'free_count': free_count,
            'email_sent_count': email_sent_count,
            'email_failed_count': email_failed_count,
            'avg_days': round(avg_days, 1),
            'avg_books': round(avg_books, 1),
            'recent_deletions': recent_deletions,
        }

        return render(request, 'admin/account_deletion_dashboard.html', context)

    # ===== PERSONALIZAÇÃO =====

    class Media:
        css = {
            'all': ('admin/css/account_deletion_admin.css',)
        }

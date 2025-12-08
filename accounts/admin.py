"""
Admin para os models de Accounts - Sistema de Biblioteca Pessoal
CGBookStore v3
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, BookShelf, ReadingProgress, BookReview, CampaignNotification, AccountDeletion


# Inline para UserProfile no User Admin
class UserProfileInline(admin.StackedInline):
    """Inline do perfil do usuário na admin de User."""
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'

    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('avatar', 'banner', 'bio', 'favorite_genre', 'theme_preference')
        }),
        ('Gamificação', {
            'fields': ('total_xp', 'level', 'reading_goal_year', 'streak_days'),
            'classes': ('collapse',)
        }),
        ('Premium', {
            'fields': ('is_premium', 'premium_expires_at'),
            'classes': ('collapse',)
        }),
        ('Privacidade', {
            'fields': ('is_profile_public', 'allow_followers'),
            'classes': ('collapse',)
        }),
    )


# Estender o UserAdmin padrão
class UserAdmin(BaseUserAdmin):
    """Admin customizado do User com perfil integrado."""
    inlines = (UserProfileInline,)

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'get_level', 'get_xp')

    def get_level(self, obj):
        """Exibe o nível do usuário."""
        if hasattr(obj, 'profile'):
            return f"Nível {obj.profile.level} - {obj.profile.level_name}"
        return "-"

    get_level.short_description = 'Nível'

    def get_xp(self, obj):
        """Exibe os pontos XP do usuário."""
        if hasattr(obj, 'profile'):
            return f"{obj.profile.total_xp} XP"
        return "0 XP"

    get_xp.short_description = 'Experiência'


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para UserProfile."""

    list_display = ('user', 'level_display', 'total_xp', 'reading_goal_year',
                    'books_read_display', 'is_profile_public', 'is_premium', 'created_at')

    list_filter = ('is_profile_public', 'is_premium', 'allow_followers', 'created_at')

    search_fields = ('user__username', 'user__email', 'bio')

    readonly_fields = ('created_at', 'updated_at', 'level_display',
                       'books_read_display', 'goal_percentage_display',
                       'streak_display', 'total_pages_read', 'books_read_count')

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Perfil Visual', {
            'fields': ('avatar', 'banner', 'bio', 'theme_preference', 'favorite_genre')
        }),
        ('Gamificação', {
            'fields': ('total_xp', 'level_display', 'streak_display', 'reading_goal_year',
                       'books_read_display', 'goal_percentage_display',
                       'books_read_count', 'total_pages_read')
        }),
        ('Premium', {
            'fields': ('is_premium', 'premium_expires_at')
        }),
        ('Privacidade', {
            'fields': ('is_profile_public', 'allow_followers')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'last_activity_date'),
            'classes': ('collapse',)
        }),
    )

    def level_display(self, obj):
        """Exibe o nível com badge colorido."""
        colors = {
            range(1, 6): '#6c757d',    # Cinza: Níveis 1-5
            range(6, 11): '#007bff',   # Azul: Níveis 6-10
            range(11, 16): '#28a745',  # Verde: Níveis 11-15
            range(16, 21): '#ffc107',  # Amarelo: Níveis 16-20
            range(21, 31): '#dc3545',  # Vermelho: Níveis 21-30
        }

        color = '#6c757d'
        for level_range, range_color in colors.items():
            if obj.level in level_range:
                color = range_color
                break

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 4px; font-weight: bold;">Nível {} - {}</span>',
            color, obj.level, obj.level_name
        )

    level_display.short_description = 'Nível'

    def streak_display(self, obj):
        """Exibe o streak de dias consecutivos."""
        if obj.streak_days > 0:
            return format_html(
                '<span style="color: #ff6b35; font-weight: bold;">🔥 {} dias</span>',
                obj.streak_days
            )
        return "Sem streak"

    streak_display.short_description = 'Streak'

    def books_read_display(self, obj):
        """Exibe quantidade de livros lidos este ano."""
        count = obj.books_read_this_year()
        return f"{count} livros"

    books_read_display.short_description = 'Livros Lidos (ano)'

    def goal_percentage_display(self, obj):
        """Exibe percentual da meta com barra de progresso."""
        percentage = obj.goal_percentage()
        color = '#28a745' if percentage >= 100 else '#007bff'
        percentage_str = f'{percentage:.1f}%'
        return format_html(
            '<div style="width: 200px; background: #e9ecef; border-radius: 4px; '
            'overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; '
            'text-align: center; padding: 4px; font-weight: bold;">{}</div>'
            '</div>',
            min(percentage, 100), color, percentage_str
        )
    goal_percentage_display.short_description = 'Meta do Ano'


@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    """Admin para BookShelf."""

    list_display = ('user', 'book', 'shelf_type_display', 'date_added',
                    'is_public', 'has_notes')

    list_filter = ('shelf_type', 'is_public', 'date_added')

    search_fields = ('user__username', 'book__title', 'book__author__name',
                     'notes', 'custom_shelf_name')

    readonly_fields = ('date_added',)

    autocomplete_fields = ['user', 'book']

    fieldsets = (
        ('Básico', {
            'fields': ('user', 'book', 'shelf_type', 'custom_shelf_name')
        }),
        ('Detalhes', {
            'fields': ('notes', 'is_public', 'date_added')
        }),
        ('Tracking de Leitura', {
            'fields': ('started_reading', 'finished_reading'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_public', 'mark_as_private', 'move_to_read']

    def shelf_type_display(self, obj):
        """Exibe o tipo de prateleira com badge."""
        colors = {
            'favorites': '#dc3545',
            'to_read': '#007bff',
            'reading': '#ffc107',
            'read': '#28a745',
            'abandoned': '#6c757d',
            'custom': '#17a2b8'
        }
        color = colors.get(obj.shelf_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color, obj.get_shelf_display()
        )

    shelf_type_display.short_description = 'Prateleira'

    def has_notes(self, obj):
        """Indica se tem notas."""
        return '✓' if obj.notes else '✗'

    has_notes.short_description = 'Notas'

    def mark_as_public(self, request, queryset):
        """Ação para marcar como público."""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} livros marcados como públicos.')

    mark_as_public.short_description = 'Marcar como público'

    def mark_as_private(self, request, queryset):
        """Ação para marcar como privado."""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} livros marcados como privados.')

    mark_as_private.short_description = 'Marcar como privado'

    def move_to_read(self, request, queryset):
        """Ação para mover para 'Lidos'."""
        updated = queryset.update(shelf_type='read')
        self.message_user(request, f'{updated} livros movidos para "Lidos".')

    move_to_read.short_description = 'Mover para "Lidos"'


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    """Admin para ReadingProgress."""

    list_display = ('user', 'book', 'progress_display', 'pages_display',
                    'reading_time_display', 'last_updated')

    list_filter = ('started_at', 'finished_at', 'last_updated')

    search_fields = ('user__username', 'book__title', 'book__author__name')

    readonly_fields = ('started_at', 'last_updated', 'percentage_display',
                       'reading_time_display', 'pages_per_day_display',
                       'estimated_finish_display')

    autocomplete_fields = ['user', 'book']

    fieldsets = (
        ('Básico', {
            'fields': ('user', 'book')
        }),
        ('Progresso', {
            'fields': ('current_page', 'total_pages', 'percentage_display')
        }),
        ('Datas', {
            'fields': ('started_at', 'finished_at', 'last_updated')
        }),
        ('Estatísticas', {
            'fields': ('reading_time_display', 'pages_per_day_display',
                       'estimated_finish_display'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('reading_notes',),
            'classes': ('collapse',)
        }),
    )

    def progress_display(self, obj):
        """Exibe progresso com barra."""
        percentage = obj.percentage
        color = '#28a745' if percentage >= 100 else '#007bff'
        percentage_str = f'{percentage:.1f}%'
        return format_html(
            '<div style="width: 150px; background: #e9ecef; border-radius: 4px; '
            'overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; '
            'text-align: center; padding: 2px; font-size: 11px; font-weight: bold;">'
            '{}</div></div>',
            min(percentage, 100), color, percentage_str
        )
    progress_display.short_description = 'Progresso'

    def percentage_display(self, obj):
        """Exibe percentual numérico."""
        return f"{obj.percentage}%"

    percentage_display.short_description = 'Percentual'

    def pages_display(self, obj):
        """Exibe páginas."""
        return f"{obj.current_page} / {obj.total_pages}"

    pages_display.short_description = 'Páginas'

    def reading_time_display(self, obj):
        """Exibe tempo de leitura."""
        days = obj.reading_time_days
        if days == 0:
            return "Hoje"
        elif days == 1:
            return "1 dia"
        else:
            return f"{days} dias"

    reading_time_display.short_description = 'Tempo de Leitura'

    def pages_per_day_display(self, obj):
        """Exibe média de páginas por dia."""
        return f"{obj.pages_per_day} pág/dia"

    pages_per_day_display.short_description = 'Páginas por Dia'

    def estimated_finish_display(self, obj):
        """Exibe estimativa de conclusão."""
        date = obj.estimated_finish_date
        if date and not obj.is_finished:
            return date.strftime('%d/%m/%Y')
        return "-"

    estimated_finish_display.short_description = 'Previsão de Término'


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    """Admin para BookReview."""

    list_display = ('user', 'book', 'rating_display', 'is_public',
                    'would_recommend', 'contains_spoilers', 'created_at')

    list_filter = ('rating', 'is_public', 'would_recommend',
                   'contains_spoilers', 'created_at')

    search_fields = ('user__username', 'book__title', 'book__author__name',
                     'title', 'review_text')

    readonly_fields = ('created_at', 'updated_at', 'helpful_count')

    autocomplete_fields = ['user', 'book']

    fieldsets = (
        ('Básico', {
            'fields': ('user', 'book', 'rating')
        }),
        ('Resenha', {
            'fields': ('title', 'review_text')
        }),
        ('Configurações', {
            'fields': ('is_public', 'contains_spoilers', 'would_recommend')
        }),
        ('Estatísticas', {
            'fields': ('helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_public', 'mark_as_private']

    def rating_display(self, obj):
        """Exibe avaliação com estrelas."""
        return format_html(
            '<span style="color: #ffc107; font-size: 16px;">{}</span>',
            obj.rating_stars
        )

    rating_display.short_description = 'Avaliação'

    def mark_as_public(self, request, queryset):
        """Ação para marcar como público."""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} resenhas marcadas como públicas.')

    mark_as_public.short_description = 'Marcar como público'

    def mark_as_private(self, request, queryset):
        """Ação para marcar como privado."""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} resenhas marcadas como privadas.')

    mark_as_private.short_description = 'Marcar como privado'


@admin.register(CampaignNotification)
class CampaignNotificationAdmin(admin.ModelAdmin):
    """Admin para CampaignNotification."""

    list_display = ('user', 'campaign', 'notification_type', 'is_read_display',
                    'priority', 'created_at_display')

    list_filter = ('notification_type', 'is_read', 'priority', 'created_at')

    search_fields = ('user__username', 'campaign__name', 'message')

    readonly_fields = ('created_at', 'read_at', 'campaign', 'campaign_grant',
                       'user', 'notification_type', 'message')

    fieldsets = (
        ('Informações', {
            'fields': ('user', 'campaign', 'campaign_grant', 'notification_type')
        }),
        ('Conteúdo', {
            'fields': ('message', 'priority', 'action_url', 'action_text')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
        ('Dados Extras', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def is_read_display(self, obj):
        """Exibe status de leitura com ícone."""
        if obj.is_read:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Lida</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">● Não lida</span>'
        )

    is_read_display.short_description = 'Status'

    def created_at_display(self, obj):
        """Exibe data de criação formatada."""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    created_at_display.short_description = 'Criada em'

    def mark_as_read(self, request, queryset):
        """Marca notificações como lidas."""
        count = 0
        for notification in queryset:
            if notification.mark_as_read():
                count += 1
        self.message_user(request, f'{count} notificação(ões) marcada(s) como lida(s).')

    mark_as_read.short_description = 'Marcar como lida'

    def mark_as_unread(self, request, queryset):
        """Marca notificações como não lidas."""
        count = 0
        for notification in queryset:
            if notification.mark_as_unread():
                count += 1
        self.message_user(request, f'{count} notificação(ões) marcada(s) como não lida(s).')

    mark_as_unread.short_description = 'Marcar como não lida'


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

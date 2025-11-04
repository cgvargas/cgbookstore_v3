"""
Admin para os models de Accounts - Sistema de Biblioteca Pessoal
CGBookStore v3
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, BookShelf, ReadingProgress, BookReview, CampaignNotification


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
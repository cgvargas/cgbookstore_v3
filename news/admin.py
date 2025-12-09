from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Tag, Article, Quiz, QuizQuestion, QuizOption, Newsletter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_badge', 'order', 'is_active', 'articles_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Aparência', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def colored_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">'
            '<i class="{}"></i> {}</span>',
            obj.color,
            obj.icon if obj.icon else 'fas fa-circle',
            obj.name
        )
    colored_badge.short_description = 'Badge'

    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Artigos'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'articles_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Artigos'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'content_type_badge',
        'category',
        'author',
        'priority_badge',
        'is_published',
        'published_at',
        'views_count'
    ]
    list_filter = [
        'content_type',
        'category',
        'is_published',
        'is_featured',
        'is_breaking',
        'priority',
        'published_at',
        'created_at'
    ]
    search_fields = ['title', 'subtitle', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    list_per_page = 25

    readonly_fields = ['views_count', 'created_at', 'updated_at', 'image_preview']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'subtitle', 'content_type')
        }),
        ('Conteúdo', {
            'fields': ('excerpt', 'content')
        }),
        ('Mídia', {
            'fields': ('featured_image', 'image_preview', 'image_caption', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Relacionamentos', {
            'fields': ('category', 'tags', 'author', 'related_book'),
            'classes': ('collapse',)
        }),
        ('Prioridade e Destaque', {
            'fields': ('priority', 'is_featured', 'is_breaking'),
            'description': 'Configure a prioridade e destacamento do artigo'
        }),
        ('Publicação', {
            'fields': ('is_published', 'published_at')
        }),
        ('Evento (Opcional)', {
            'fields': ('event_date', 'event_location', 'event_link'),
            'classes': ('collapse',),
            'description': 'Preencha apenas se o tipo de conteúdo for "Evento"'
        }),
        ('Estatísticas', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_articles', 'unpublish_articles', 'mark_as_featured', 'mark_as_breaking']

    def content_type_badge(self, obj):
        colors = {
            'news': '#3498db',
            'interview': '#9b59b6',
            'event': '#e74c3c',
            'announcement': '#e67e22',
            'tip': '#f39c12',
            'highlight': '#f1c40f',
            'schedule': '#1abc9c',
            'article': '#34495e',
            'guide': '#16a085',
            'review': '#27ae60',
        }
        color = colors.get(obj.content_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_content_type_display()
        )
    content_type_badge.short_description = 'Tipo'

    def priority_badge(self, obj):
        colors = {
            1: '#95a5a6',
            2: '#3498db',
            3: '#f39c12',
            4: '#e67e22',
            5: '#e74c3c',
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridade'

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 5px;" />',
                obj.featured_image.url
            )
        return "Sem imagem"
    image_preview.short_description = 'Preview da Imagem'

    def publish_articles(self, request, queryset):
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f'{updated} artigo(s) publicado(s) com sucesso.')
    publish_articles.short_description = 'Publicar artigos selecionados'

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} artigo(s) despublicado(s) com sucesso.')
    unpublish_articles.short_description = 'Despublicar artigos selecionados'

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} artigo(s) marcado(s) como destaque.')
    mark_as_featured.short_description = 'Marcar como destaque'

    def mark_as_breaking(self, request, queryset):
        updated = queryset.update(is_breaking=True)
        self.message_user(request, f'{updated} artigo(s) marcado(s) como última hora.')
    mark_as_breaking.short_description = 'Marcar como última hora'


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4
    fields = ['option_text', 'is_correct', 'order']


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1
    fields = ['question_text', 'question_image', 'explanation', 'order']
    show_change_link = True


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'order', 'options_count']
    list_filter = ['quiz']
    search_fields = ['question_text', 'explanation']
    inlines = [QuizOptionInline]

    def options_count(self, obj):
        return obj.options.count()
    options_count.short_description = 'Opções'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'times_completed', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['times_completed', 'created_at', 'updated_at']
    inlines = [QuizQuestionInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'description', 'featured_image')
        }),
        ('Relacionamentos', {
            'fields': ('category', 'related_article')
        }),
        ('Configurações', {
            'fields': ('is_active', 'show_results_immediately')
        }),
        ('Estatísticas', {
            'fields': ('times_completed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    date_hierarchy = 'subscribed_at'

    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} inscrição(ões) ativada(s).')
    activate_subscriptions.short_description = 'Ativar inscrições'

    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} inscrição(ões) desativada(s).')
    deactivate_subscriptions.short_description = 'Desativar inscrições'

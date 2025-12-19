from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Category, Tag, Article, Quiz, QuizQuestion, QuizOption, Newsletter, QuizAttempt, NewsSource, NewsAgentConfig


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
        'ai_badge',
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
        'ai_generated',
        'priority',
        'published_at',
        'created_at'
    ]
    search_fields = ['title', 'subtitle', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    list_per_page = 25

    class Media:
        css = {
            'all': ('css/ckeditor5_dark.css',)
        }

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
        ('Metadados de IA', {
            'fields': ('ai_generated', 'ai_model', 'ai_processing_time', 'source_url', 'source_name', 'meta_description'),
            'classes': ('collapse',),
            'description': 'Campos preenchidos automaticamente quando o artigo é gerado por IA'
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

    def ai_badge(self, obj):
        if obj.ai_generated:
            return format_html(
                '<span style="background-color: #9b59b6; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">'
                '🤖 IA</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">'
            '✍️ Manual</span>'
        )
    ai_badge.short_description = 'Origem'


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


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score_display', 'xp_earned', 'level_change', 'completed_at']
    list_filter = ['leveled_up', 'completed_at', 'quiz']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['user', 'quiz', 'score', 'total_questions', 'score_percentage',
                       'xp_earned', 'leveled_up', 'level_before', 'level_after', 'completed_at']
    date_hierarchy = 'completed_at'
    list_per_page = 50

    def has_add_permission(self, request):
        return False  # Não permitir adicionar manualmente

    def score_display(self, obj):
        color = '#27ae60' if obj.score_percentage >= 70 else '#e67e22' if obj.score_percentage >= 50 else '#e74c3c'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
            '{}/{} ({}%)</span>',
            color,
            obj.score,
            obj.total_questions,
            int(obj.score_percentage)
        )
    score_display.short_description = 'Pontuação'

    def level_change(self, obj):
        if obj.leveled_up:
            return format_html(
                '<span style="color: #f39c12; font-weight: bold;">⬆️ {} → {}</span>',
                obj.level_before,
                obj.level_after
            )
        return f'Nível {obj.level_after}'
    level_change.short_description = 'Nível'


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


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'source_type',
        'is_active',
        'priority',
        'success_rate_display',
        'last_fetch_at',
        'last_fetch_status'
    ]
    list_filter = ['is_active', 'source_type', 'priority']
    search_fields = ['name', 'url']
    list_editable = ['is_active', 'priority']
    readonly_fields = ['last_fetch_at', 'last_fetch_status', 'total_items_fetched', 'total_items_published', 'created_at', 'updated_at']
    list_per_page = 25

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'url', 'source_type')
        }),
        ('Configurações', {
            'fields': ('is_active', 'priority')
        }),
        ('Filtros de Palavras-chave', {
            'fields': ('keywords_include', 'keywords_exclude'),
            'classes': ('collapse',),
            'description': 'Configure palavras-chave para filtrar notícias relevantes'
        }),
        ('Estatísticas', {
            'fields': ('last_fetch_at', 'last_fetch_status', 'total_items_fetched', 'total_items_published'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def success_rate_display(self, obj):
        rate = obj.success_rate
        if obj.total_items_fetched == 0:
            return '-'
        color = '#27ae60' if rate >= 50 else '#e67e22' if rate >= 25 else '#e74c3c'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            f"{float(rate):.1f}"
        )
    success_rate_display.short_description = 'Taxa de Sucesso'


@admin.register(NewsAgentConfig)
class NewsAgentConfigAdmin(admin.ModelAdmin):
    """Admin para configuração do Agente de Notícias."""
    
    list_display = ['name', 'mode_badge', 'schedule_display', 'last_run_display', 'total_articles_generated', 'is_active']
    list_filter = ['mode', 'is_active', 'schedule']
    
    fieldsets = (
        ('🎛️ Configuração Geral', {
            'fields': ('name', 'mode', 'is_active'),
            'description': 'Defina o modo de operação do agente de notícias'
        }),
        ('📊 Configurações de Pesquisa', {
            'fields': ('articles_per_run', 'hours_lookback', 'include_images'),
            'description': 'Quantos artigos gerar e de qual período'
        }),
        ('⏰ Agendamento (Modo Automático)', {
            'fields': ('schedule', 'schedule_hour', 'schedule_minute'),
            'classes': ('collapse',),
            'description': 'Configure quando o agente deve rodar automaticamente'
        }),
        ('🎯 Temas e Filtros', {
            'fields': ('specific_themes', 'category_filter'),
            'classes': ('collapse',),
            'description': 'Defina temas específicos para pesquisar'
        }),
        ('📈 Estatísticas', {
            'fields': ('last_run', 'last_run_articles', 'total_articles_generated'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['last_run', 'last_run_articles', 'total_articles_generated']
    
    actions = ['run_agent_now']
    
    def mode_badge(self, obj):
        colors = {
            'manual': '#3498db',
            'automatic': '#27ae60',
            'paused': '#95a5a6',
        }
        icons = {
            'manual': '🔧',
            'automatic': '🤖',
            'paused': '⏸️',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px;">{} {}</span>',
            colors.get(obj.mode, '#333'),
            icons.get(obj.mode, ''),
            obj.get_mode_display().split(' ')[-1]
        )
    mode_badge.short_description = 'Modo'
    
    def schedule_display(self, obj):
        return f"🕐 {obj.get_schedule_display()} às {obj.schedule_hour:02d}:{obj.schedule_minute:02d}"
    schedule_display.short_description = 'Agendamento'
    
    def last_run_display(self, obj):
        if not obj.last_run:
            return format_html('<span style="color: #95a5a6;">Nunca executado</span>')
        diff = timezone.now() - obj.last_run
        if diff.days > 0:
            ago = f"{diff.days} dias atrás"
        elif diff.seconds > 3600:
            ago = f"{diff.seconds // 3600}h atrás"
        else:
            ago = f"{diff.seconds // 60}min atrás"
        return format_html(
            '<span title="{}">📅 {} ({} artigos)</span>',
            obj.last_run.strftime('%d/%m/%Y %H:%M'),
            ago,
            obj.last_run_articles
        )
    last_run_display.short_description = 'Última Execução'
    
    def run_agent_now(self, request, queryset):
        """Ação para executar o agente imediatamente."""
        from django.core.management import call_command
        from io import StringIO
        
        config = queryset.first()
        if not config:
            self.message_user(request, "Selecione uma configuração", level=messages.WARNING)
            return
        
        try:
            out = StringIO()
            call_command(
                'generate_news_posts',
                limit=config.articles_per_run,
                skip_images=not config.include_images,
                stdout=out
            )
            
            # Atualizar estatísticas
            config.last_run = timezone.now()
            config.save()
            
            self.message_user(
                request, 
                f"✅ Agente executado! Verifique os artigos gerados.",
                level=messages.SUCCESS
            )
        except Exception as e:
            self.message_user(request, f"❌ Erro: {str(e)}", level=messages.ERROR)
    
    run_agent_now.short_description = "🚀 Executar Agente Agora"
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_run_button'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """Ao salvar, reinicia o scheduler com as novas configurações."""
        super().save_model(request, obj, form, change)
        
        # Reiniciar scheduler com novas configurações
        try:
            from news.scheduler import restart_scheduler
            restart_scheduler()
            self.message_user(request, "🔄 Agendamento atualizado!", level=messages.INFO)
        except Exception as e:
            self.message_user(request, f"⚠️ Schedulter não iniciado: {e}", level=messages.WARNING)



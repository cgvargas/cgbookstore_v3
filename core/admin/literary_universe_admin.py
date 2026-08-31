# core/admin/literary_universe_admin.py
"""
Admin completo para Universos Literários — Evolução v2.
HUB de conhecimento com score de qualidade Bronze/Prata/Ouro/Platina,
checklist visual, estatísticas automáticas e ação Duplicar Universo.
"""

from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.text import slugify
from django.http import HttpResponseRedirect
from django.urls import reverse
from core.models import (
    LiteraryUniverse,
    UniverseContentItem,
    UniverseBanner,
    UniverseReadingOrder,
    UniverseTimelineEvent,
    UniverseFAQ,
    UniverseCharacter,
    UniverseCollection,
)
from core.admin.image_rights_admin import ImageRightsRecordInline
from core.services.image_rights_service import ImageRightsAuditService


# ==============================================================================
# INLINES
# ==============================================================================

class UniverseContentItemInline(admin.TabularInline):
    """Inline para itens de conteúdo (games, adaptações, etc.)."""
    model = UniverseContentItem
    extra = 0
    fields = [
        'content_type', 'title', 'url', 'thumbnail',
        'year', 'studio', 'media_status', 'platform',
        'display_order', 'is_active'
    ]
    ordering = ['content_type', 'display_order']
    classes = ['collapse']
    verbose_name = "Adaptação / Conteúdo"
    verbose_name_plural = "🎬 Adaptações e Conteúdo Externo"


class UniverseBannerInline(admin.TabularInline):
    """Inline para banners promocionais."""
    model = UniverseBanner
    extra = 0
    fields = ['title', 'position', 'size', 'image', 'is_active', 'display_order']
    ordering = ['position', 'display_order']
    classes = ['collapse']
    verbose_name_plural = "🖼️ Banners Promocionais"


class UniverseReadingOrderInline(admin.TabularInline):
    """Inline para ordem de leitura."""
    model = UniverseReadingOrder
    extra = 0
    fields = [
        'order_number', 'title', 'book_type', 'book',
        'chronological_order', 'publication_year', 'is_essential', 'notes'
    ]
    ordering = ['order_number']
    autocomplete_fields = ['book']
    verbose_name_plural = "📖 Ordem de Leitura"


class UniverseTimelineEventInline(admin.StackedInline):
    """Inline para eventos da cronologia."""
    model = UniverseTimelineEvent
    extra = 0
    fields = [
        ('title', 'importance'),
        ('era', 'approximate_date', 'chronological_position'),
        'description',
        ('image', 'is_active'),
    ]
    ordering = ['chronological_position']
    classes = ['collapse']
    verbose_name_plural = "⏳ Cronologia"


class UniverseFAQInline(admin.TabularInline):
    """Inline para perguntas frequentes."""
    model = UniverseFAQ
    extra = 0
    fields = ['question', 'answer', 'display_order', 'is_active']
    ordering = ['display_order']
    verbose_name_plural = "❓ Perguntas Frequentes (FAQ)"


class UniverseCharacterInline(admin.TabularInline):
    """Inline para personagens (preparação futura)."""
    model = UniverseCharacter
    extra = 0
    fields = ['name', 'role', 'description', 'image', 'display_order', 'is_active']
    ordering = ['display_order']
    classes = ['collapse']
    verbose_name_plural = "👤 Personagens (Preparação Futura)"


# ==============================================================================
# ADMIN PRINCIPAL — LiteraryUniverse
# ==============================================================================

@admin.register(LiteraryUniverse)
class LiteraryUniverseAdmin(admin.ModelAdmin):
    """Admin completo para Universos Literários com score de qualidade e duplicação."""
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['theme_color_primary', 'theme_color_secondary']:
            kwargs['widget'] = forms.TextInput(attrs={
                'type': 'color',
                'style': 'height:38px; width:80px; padding:2px; cursor:pointer;'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    list_display = [
        'title', 
        'author', 
        'quality_badge',
        'is_active', 
        'featured_on_home',
        'show_in_menu',
        'display_order',
        'stats_summary',
        'color_preview',
        'view_link',
    ]
    
    list_filter = ['is_active', 'show_in_menu', 'featured_on_home', 'collection']
    list_editable = ['is_active', 'show_in_menu', 'featured_on_home', 'display_order']
    search_fields = ['title', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'additional_authors', 'videos', 'books']
    filter_horizontal = ['articles', 'quizzes', 'related_universes', 'related_categories']
    actions = ['duplicate_universe']
    
    inlines = [
        UniverseReadingOrderInline,
        UniverseFAQInline,
        UniverseTimelineEventInline,
        UniverseContentItemInline,
        UniverseCharacterInline,
        UniverseBannerInline,
        ImageRightsRecordInline,
    ]
    
    fieldsets = (
        ('📋 Informações Gerais', {
            'fields': (
                'title', 'slug', 'author', 'additional_authors',
                'logo',
                ('is_active', 'featured_on_home', 'show_in_menu', 'display_order'),
                'collection',
            )
        }),
        ('🎨 Visual / Tema', {
            'fields': (
                'hero_banner_image', 
                ('hero_banner_position_horizontal', 'hero_banner_position_vertical'),
                'hero_banner_overlay_opacity',
                'hero_icon', 
                ('theme_color_primary', 'theme_color_secondary')
            ),
        }),
        ('📝 Textos da Página', {
            'fields': ('page_subtitle', 'page_title', 'page_description')
        }),
        ('🔍 SEO e Open Graph', {
            'fields': (
                ('meta_title', 'meta_description'),
                ('og_title', 'og_description'),
                'og_image',
                'canonical_url',
            ),
            'classes': ('collapse',),
            'description': 'Configurações de SEO, Open Graph e compartilhamento social.'
        }),
        ('📚 Conteúdo Associado', {
            'fields': ('books', 'videos', 'articles', 'quizzes'),
            'description': (
                'Selecione livros, vídeos, artigos e quizzes para exibir neste universo. '
                'Livros do autor principal são incluídos automaticamente.'
            )
        }),
        ('🔗 Relações e Cross-Linking', {
            'fields': ('related_universes', 'related_categories'),
            'classes': ('collapse',),
            'description': 'Relações com outros universos e categorias para melhorar navegação e SEO interno.'
        }),
        ('🎛️ Layout — Livros', {
            'fields': (('books_card_style', 'books_container_style'),),
            'classes': ('collapse',),
        }),
        ('🎛️ Layout — Artigos', {
            'fields': (('articles_card_style', 'articles_container_style'),),
            'classes': ('collapse',),
        }),
        ('🎛️ Layout — Vídeos', {
            'fields': (('videos_card_style', 'videos_container_style'),),
            'classes': ('collapse',),
        }),
        ('🎛️ Layout — Conteúdo Adicional', {
            'fields': (('content_card_style', 'content_container_style'),),
            'classes': ('collapse',),
        }),
        ('📊 Estatísticas e Qualidade (somente leitura)', {
            'fields': ('stats_display', 'quality_display'),
            'description': 'Dados calculados automaticamente. Não editáveis.'
        }),
    )
    
    readonly_fields = ['stats_display', 'quality_display']
    
    # === CAMPOS CALCULADOS PARA LIST_DISPLAY ===
    
    def quality_badge(self, obj):
        """Exibe badge de qualidade Bronze/Prata/Ouro/Platina."""
        quality = obj.get_quality_score()
        return format_html(
            '<span style="display:inline-flex; align-items:center; gap:4px; '
            'padding:3px 10px; border-radius:12px; font-size:0.8em; font-weight:600; '
            'background:{}20; color:{}; border:1px solid {}40;">'
            '{} {} ({}%)</span>',
            quality['color'], quality['color'], quality['color'],
            quality['icon'], quality['label'], quality['score']
        )
    quality_badge.short_description = 'Qualidade'
    
    def stats_summary(self, obj):
        """Resumo de estatísticas na listagem."""
        stats = obj.get_stats()
        parts = []
        if stats['books_count']:
            parts.append(f"📚{stats['books_count']}")
        if stats['articles_count']:
            parts.append(f"📰{stats['articles_count']}")
        if stats['videos_count']:
            parts.append(f"🎬{stats['videos_count']}")
        if stats['faqs_count']:
            parts.append(f"❓{stats['faqs_count']}")
        return ' '.join(parts) or '—'
    stats_summary.short_description = 'Conteúdo'
    
    def color_preview(self, obj):
        """Exibe preview das cores do tema."""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px; margin-right: 5px;"></span>'
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px;"></span>',
            obj.theme_color_primary,
            obj.theme_color_secondary
        )
    color_preview.short_description = 'Cores'
    
    def view_link(self, obj):
        """Link para visualizar a página."""
        if obj.is_active:
            return format_html(
                '<a href="/universo/{}/" target="_blank" class="button">'
                '<i class="fas fa-external-link-alt"></i> Ver</a>',
                obj.slug
            )
        return '—'
    view_link.short_description = 'Visualizar'
    
    # === CAMPOS READONLY PARA O FORMULÁRIO ===
    
    def stats_display(self, obj):
        """Exibe estatísticas completas no formulário."""
        if not obj.pk:
            return 'Salve o universo para ver as estatísticas.'
        
        stats = obj.get_stats()
        rows = [
            ('📚 Livros', stats['books_count']),
            ('👤 Autores', stats['authors_count']),
            ('📰 Artigos', stats['articles_count']),
            ('🎬 Vídeos', stats['videos_count']),
            ('🧩 Quizzes', stats['quizzes_count']),
            ('❓ FAQs', stats['faqs_count']),
            ('⏳ Eventos na Cronologia', stats['timeline_count']),
            ('📖 Itens na Ordem de Leitura', stats['reading_order_count']),
            ('🎭 Adaptações/Games', stats['adaptations_count']),
            ('👤 Personagens', stats['characters_count']),
            ('📄 Total de Páginas', f"{stats['total_pages']:,}"),
        ]
        
        html = '<table style="border-collapse:collapse; font-size:13px;">'
        for label, value in rows:
            color = '#28a745' if (isinstance(value, int) and value > 0) else '#6c757d'
            html += (
                f'<tr>'
                f'<td style="padding:3px 12px 3px 0; color:#555;">{label}</td>'
                f'<td style="padding:3px 0; font-weight:600; color:{color};">{value}</td>'
                f'</tr>'
            )
        html += '</table>'
        return format_html(html)
    stats_display.short_description = 'Estatísticas do Universo'
    
    def quality_display(self, obj):
        """Exibe painel de qualidade com checklist visual no formulário."""
        if not obj.pk:
            return 'Salve o universo para ver a avaliação de qualidade.'
        
        quality = obj.get_quality_score()
        
        # Cabeçalho do tier
        html = format_html(
            '<div style="margin-bottom:16px; padding:12px 16px; border-radius:10px; '
            'background:{}15; border:2px solid {}40; display:inline-flex; '
            'align-items:center; gap:8px;">'
            '<span style="font-size:24px;">{}</span>'
            '<span style="font-size:18px; font-weight:700; color:{};">{}</span>'
            '<span style="font-size:14px; color:#666; margin-left:8px;">— {} pontos de 100</span>'
            '</div>',
            quality['color'], quality['color'],
            quality['icon'],
            quality['color'], quality['label'],
            quality['score']
        )
        
        # Barra de progresso
        html += format_html(
            '<div style="width:100%; max-width:500px; height:8px; background:#e9ecef; '
            'border-radius:4px; margin-bottom:16px; overflow:hidden;">'
            '<div style="width:{}%; height:100%; background:{}; border-radius:4px; '
            'transition:width 0.3s;"></div></div>',
            quality['score'], quality['color']
        )
        
        # Checklist por grupo
        groups = {}
        for name, achieved, weight, group in quality['checklist']:
            if group not in groups:
                groups[group] = []
            groups[group].append((name, achieved, weight))
        
        html += '<div style="display:flex; flex-wrap:wrap; gap:16px;">'
        for group_name, items in groups.items():
            html += (
                f'<div style="flex:1; min-width:200px; background:#f8f9fa; '
                f'border-radius:8px; padding:12px;">'
                f'<div style="font-weight:600; margin-bottom:8px; color:#333;">{group_name}</div>'
            )
            for name, achieved, weight in items:
                icon = '✅' if achieved else '⬜'
                color = '#28a745' if achieved else '#adb5bd'
                html += (
                    f'<div style="padding:2px 0; font-size:12px; color:{color};">'
                    f'{icon} {name} <span style="opacity:0.5">({weight}pt)</span>'
                    f'</div>'
                )
            html += '</div>'
        html += '</div>'
        
        return format_html(html)
    quality_display.short_description = 'Avaliação de Qualidade'
    
    # === AÇÃO: DUPLICAR UNIVERSO ===
    
    @admin.action(description='📋 Duplicar universo(s) selecionado(s)')
    def duplicate_universe(self, request, queryset):
        """Cria cópias dos universos selecionados com relacionamentos vazios."""
        for universe in queryset:
            # Gerar novo slug único
            base_slug = f'{universe.slug}-copia'
            new_slug = base_slug
            counter = 1
            while LiteraryUniverse.objects.filter(slug=new_slug).exists():
                new_slug = f'{base_slug}-{counter}'
                counter += 1
            
            # Criar cópia (sem PK, M2M ou inlines)
            new_universe = LiteraryUniverse(
                title=f'{universe.title} (Cópia)',
                slug=new_slug,
                author=universe.author,
                is_active=False,  # Inativo por padrão para revisão
                featured_on_home=False,
                display_order=universe.display_order,
                show_in_menu=False,
                # Visual
                theme_color_primary=universe.theme_color_primary,
                theme_color_secondary=universe.theme_color_secondary,
                hero_icon=universe.hero_icon,
                hero_banner_overlay_opacity=universe.hero_banner_overlay_opacity,
                hero_banner_position_vertical=universe.hero_banner_position_vertical,
                hero_banner_position_horizontal=universe.hero_banner_position_horizontal,
                # Layout
                books_card_style=universe.books_card_style,
                books_container_style=universe.books_container_style,
                articles_card_style=universe.articles_card_style,
                articles_container_style=universe.articles_container_style,
                videos_card_style=universe.videos_card_style,
                videos_container_style=universe.videos_container_style,
                content_card_style=universe.content_card_style,
                content_container_style=universe.content_container_style,
                # Textos (vazios para forçar preenchimento)
                page_title=f'{universe.title} (Cópia)',
                page_subtitle=universe.page_subtitle,
                page_description='',
                # SEO vazio
                meta_title='',
                meta_description='',
                # Coleção
                collection=universe.collection,
            )
            new_universe.save()
            
            self.message_user(
                request,
                f'✅ Universo "{universe.title}" duplicado com sucesso! '
                f'Novo: "{new_universe.title}" (inativo para revisão).',
                messages.SUCCESS
            )
    
    def save_model(self, request, obj, form, change):
        """Salva e invalida cache do universo."""
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)
        # Invalidar cache do universo
        from django.core.cache import cache
        cache.delete(f'literary_universe_{obj.slug}')


# ==============================================================================
# ADMINS STANDALONE (mantidos para acesso direto)
# ==============================================================================

@admin.register(UniverseContentItem)
class UniverseContentItemAdmin(admin.ModelAdmin):
    """Admin standalone para itens de conteúdo."""
    inlines = [ImageRightsRecordInline]
    list_display = [
        'title', 'universe', 'content_type', 'year',
        'media_status', 'is_active', 'display_order'
    ]
    list_filter = ['universe', 'content_type', 'media_status', 'is_active']
    search_fields = ['title', 'description', 'studio']
    list_editable = ['is_active', 'display_order']
    autocomplete_fields = ['universe']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)


@admin.register(UniverseBanner)
class UniverseBannerAdmin(admin.ModelAdmin):
    """Admin standalone para banners."""
    inlines = [ImageRightsRecordInline]
    list_display = [
        'title', 
        'universe', 
        'position', 
        'size', 
        'is_active',
        'banner_preview',
        'visibility_status',
    ]
    list_filter = ['universe', 'position', 'size', 'is_active']
    search_fields = ['title', 'alt_text']
    list_editable = ['is_active']
    autocomplete_fields = ['universe']
    
    fieldsets = (
        ('Básico', {
            'fields': ('universe', 'title', 'is_active')
        }),
        ('Imagens', {
            'fields': ('image', 'image_mobile', 'alt_text')
        }),
        ('Posicionamento', {
            'fields': ('position', 'size', 'display_order')
        }),
        ('Link', {
            'fields': ('link_url', 'link_target')
        }),
        ('Agendamento', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',),
        }),
    )
    
    def banner_preview(self, obj):
        """Preview do banner."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 50px; border-radius: 4px;">',
                obj.image.url
            )
        return '—'
    banner_preview.short_description = 'Preview'
    
    def visibility_status(self, obj):
        """Status de visibilidade baseado em datas."""
        if obj.is_visible():
            return format_html('<span style="color: green;">✓ Visível</span>')
        return format_html('<span style="color: red;">✗ Oculto</span>')
    visibility_status.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)


@admin.register(UniverseReadingOrder)
class UniverseReadingOrderAdmin(admin.ModelAdmin):
    """Admin standalone para ordem de leitura."""
    list_display = ['order_number', 'title', 'universe', 'book_type', 'is_essential', 'chronological_order']
    list_display_links = ['title']
    list_filter = ['universe', 'book_type', 'is_essential']
    search_fields = ['title', 'notes']
    list_editable = ['order_number', 'is_essential']
    autocomplete_fields = ['universe', 'book']
    ordering = ['universe', 'order_number']


@admin.register(UniverseTimelineEvent)
class UniverseTimelineEventAdmin(admin.ModelAdmin):
    """Admin standalone para eventos da cronologia."""
    inlines = [ImageRightsRecordInline]
    list_display = ['title', 'universe', 'era', 'importance', 'chronological_position', 'is_active']
    list_filter = ['universe', 'importance', 'is_active']
    search_fields = ['title', 'description', 'era']
    list_editable = ['chronological_position', 'is_active']
    autocomplete_fields = ['universe']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)


@admin.register(UniverseFAQ)
class UniverseFAQAdmin(admin.ModelAdmin):
    """Admin standalone para FAQs."""
    list_display = ['question_truncated', 'universe', 'display_order', 'is_active']
    list_filter = ['universe', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['display_order', 'is_active']
    autocomplete_fields = ['universe']
    
    def question_truncated(self, obj):
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_truncated.short_description = 'Pergunta'


@admin.register(UniverseCharacter)
class UniverseCharacterAdmin(admin.ModelAdmin):
    """Admin standalone para personagens."""
    inlines = [ImageRightsRecordInline]
    list_display = ['name', 'universe', 'role', 'display_order', 'is_active']
    list_filter = ['universe', 'role', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['display_order', 'is_active']
    autocomplete_fields = ['universe']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)


@admin.register(UniverseCollection)
class UniverseCollectionAdmin(admin.ModelAdmin):
    """Admin para coleções de universos."""
    inlines = [ImageRightsRecordInline]
    list_display = ['name', 'universes_count', 'display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    
    def universes_count(self, obj):
        count = obj.universes.count()
        return format_html(
            '<span style="font-weight:600;">{}</span> universo{}',
            count, 's' if count != 1 else ''
        )
    universes_count.short_description = 'Universos'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        ImageRightsAuditService.audit_model_admin_save(request, obj)

"""
Django Admin para o app New Authors
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EmergingAuthor,
    AuthorBook,
    Chapter,
    AuthorBookReview,
    BookFollower,
    PublisherProfile,
    PublisherInterest
)


@admin.register(EmergingAuthor)
class EmergingAuthorAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'display_name',
        'total_books',
        'total_views',
        'is_verified',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['total_views', 'total_books', 'total_followers', 'created_at', 'updated_at']

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações do Autor', {
            'fields': ('bio', 'photo')
        }),
        ('Redes Sociais', {
            'fields': ('website', 'twitter', 'instagram', 'facebook')
        }),
        ('Estatísticas', {
            'fields': ('total_views', 'total_books', 'total_followers'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    display_name.short_description = 'Nome'

    actions = ['verify_authors', 'unverify_authors']

    def verify_authors(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} autores verificados com sucesso.')
    verify_authors.short_description = 'Verificar autores selecionados'

    def unverify_authors(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} autores desverificados.')
    unverify_authors.short_description = 'Remover verificação'


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ['number', 'title', 'is_published', 'word_count', 'views_count']
    readonly_fields = ['word_count', 'views_count']


@admin.register(AuthorBook)
class AuthorBookAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'genre',
        'status',
        'rating_display',
        'views_count',
        'chapter_count',
        'published_at'
    ]
    list_filter = ['status', 'genre', 'language', 'published_at', 'created_at']
    search_fields = ['title', 'author__user__username', 'synopsis', 'description']
    readonly_fields = [
        'slug',
        'views_count',
        'likes_count',
        'rating_average',
        'rating_count',
        'created_at',
        'updated_at',
        'published_at'
    ]
    prepopulated_fields = {}
    inlines = [ChapterInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('author', 'title', 'slug', 'subtitle')
        }),
        ('Conteúdo', {
            'fields': ('synopsis', 'description', 'cover_image')
        }),
        ('Categorização', {
            'fields': ('genre', 'tags', 'language')
        }),
        ('Status', {
            'fields': ('status', 'estimated_pages')
        }),
        ('Estatísticas', {
            'fields': ('views_count', 'likes_count', 'rating_average', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_display(self, obj):
        stars = '⭐' * int(obj.rating_average)
        return format_html(
            '<span title="{}">{} ({} avaliações)</span>',
            f'{obj.rating_average:.2f}',
            stars,
            obj.rating_count
        )
    rating_display.short_description = 'Avaliação'

    def chapter_count(self, obj):
        return obj.chapters.count()
    chapter_count.short_description = 'Capítulos'

    actions = ['publish_books', 'archive_books']

    def publish_books(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f'{queryset.count()} livros publicados com sucesso.')
    publish_books.short_description = 'Publicar livros selecionados'

    def archive_books(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, f'{queryset.count()} livros arquivados.')
    archive_books.short_description = 'Arquivar livros selecionados'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = [
        'book',
        'number',
        'title',
        'is_published',
        'is_free',
        'word_count',
        'views_count',
        'published_at'
    ]
    list_filter = ['is_published', 'is_free', 'published_at', 'created_at']
    search_fields = ['title', 'book__title', 'content']
    readonly_fields = ['slug', 'word_count', 'views_count', 'preview', 'created_at', 'updated_at', 'published_at']

    fieldsets = (
        ('Livro', {
            'fields': ('book',)
        }),
        ('Informações do Capítulo', {
            'fields': ('number', 'title', 'slug')
        }),
        ('Conteúdo', {
            'fields': ('content', 'preview', 'file')
        }),
        ('Configurações', {
            'fields': ('is_published', 'is_free')
        }),
        ('Estatísticas', {
            'fields': ('word_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_chapters', 'unpublish_chapters']

    def publish_chapters(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, f'{queryset.count()} capítulos publicados com sucesso.')
    publish_chapters.short_description = 'Publicar capítulos selecionados'

    def unpublish_chapters(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f'{queryset.count()} capítulos despublicados.')
    unpublish_chapters.short_description = 'Despublicar capítulos selecionados'


@admin.register(AuthorBookReview)
class AuthorBookReviewAdmin(admin.ModelAdmin):
    list_display = [
        'book',
        'user',
        'rating_stars',
        'is_approved',
        'is_featured',
        'helpful_count',
        'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['book__title', 'user__username', 'title', 'comment']
    readonly_fields = ['helpful_count', 'report_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Avaliação', {
            'fields': ('book', 'user', 'rating')
        }),
        ('Review', {
            'fields': ('title', 'comment')
        }),
        ('Moderação', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Interações', {
            'fields': ('helpful_count', 'report_count'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span title="{}">{}</span>', f'{obj.rating} estrelas', stars)
    rating_stars.short_description = 'Avaliação'

    actions = ['approve_reviews', 'disapprove_reviews', 'feature_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} avaliações aprovadas.')
    approve_reviews.short_description = 'Aprovar avaliações selecionadas'

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} avaliações reprovadas.')
    disapprove_reviews.short_description = 'Reprovar avaliações selecionadas'

    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} avaliações destacadas.')
    feature_reviews.short_description = 'Destacar avaliações selecionadas'


@admin.register(BookFollower)
class BookFollowerAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'notify_new_chapter', 'notify_updates', 'created_at']
    list_filter = ['notify_new_chapter', 'notify_updates', 'created_at']
    search_fields = ['book__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(PublisherProfile)
class PublisherProfileAdmin(admin.ModelAdmin):
    list_display = [
        'company_name',
        'user',
        'email',
        'is_verified',
        'is_active',
        'authors_contacted',
        'created_at'
    ]
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['company_name', 'user__username', 'email', 'description']
    readonly_fields = ['authors_contacted', 'created_at', 'updated_at']

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações da Editora', {
            'fields': ('company_name', 'description', 'logo')
        }),
        ('Contato', {
            'fields': ('website', 'email', 'phone')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Estatísticas', {
            'fields': ('authors_contacted',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['verify_publishers', 'unverify_publishers']

    def verify_publishers(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} editoras verificadas com sucesso.')
    verify_publishers.short_description = 'Verificar editoras selecionadas'

    def unverify_publishers(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} editoras desverificadas.')
    unverify_publishers.short_description = 'Remover verificação'


@admin.register(PublisherInterest)
class PublisherInterestAdmin(admin.ModelAdmin):
    list_display = [
        'publisher',
        'book',
        'status',
        'created_at',
        'updated_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['publisher__company_name', 'book__title', 'message']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Interesse', {
            'fields': ('publisher', 'book', 'status')
        }),
        ('Mensagem', {
            'fields': ('message',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

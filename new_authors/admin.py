"""
Django Admin para o app New Authors
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django import forms
from .models import (
    AuthorTermsOfService,
    EmergingAuthor,
    AuthorBook,
    Chapter,
    AuthorBookReview,
    BookFollower,
    BookLike,
    PublisherProfile,
    PublisherInterest
)


@admin.register(AuthorTermsOfService)
class AuthorTermsOfServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'is_current', 'is_active', 'effective_date', 'created_at']
    list_filter = ['is_current', 'is_active', 'effective_date']
    search_fields = ['title', 'version', 'content']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'version', 'effective_date')
        }),
        ('Conteúdo', {
            'fields': ('content', 'summary_points')
        }),
        ('Status', {
            'fields': ('is_active', 'is_current')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EmergingAuthorAdminForm(forms.ModelForm):
    """Formulário customizado para o admin de EmergingAuthor"""

    GENRE_CHOICES = [
        ('fiction', 'Ficção'),
        ('romance', 'Romance'),
        ('fantasy', 'Fantasia'),
        ('scifi', 'Ficção Científica'),
        ('mystery', 'Mistério'),
        ('thriller', 'Thriller'),
        ('horror', 'Terror'),
        ('adventure', 'Aventura'),
        ('historical', 'Histórico'),
        ('biography', 'Biografia'),
        ('poetry', 'Poesia'),
        ('self_help', 'Autoajuda'),
        ('young_adult', 'Jovem Adulto'),
        ('children', 'Infantil'),
        ('other', 'Outro'),
    ]

    writing_genres = forms.MultipleChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Gêneros de Escrita',
        help_text='Selecione os gêneros literários que o autor escreve'
    )

    class Meta:
        model = EmergingAuthor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-seleciona os gêneros já salvos
        if self.instance and self.instance.pk and self.instance.writing_genres:
            self.initial['writing_genres'] = self.instance.writing_genres

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Converte a lista de strings para o formato JSON esperado
        instance.writing_genres = self.cleaned_data.get('writing_genres', [])
        if commit:
            instance.save()
        return instance


@admin.register(EmergingAuthor)
class EmergingAuthorAdmin(admin.ModelAdmin):
    form = EmergingAuthorAdminForm  # Usa o formulário customizado

    list_display = [
        'user',
        'full_name',
        'cpf',
        'status_badge',
        'total_books',
        'total_views',
        'created_at',
        'approved_at'
    ]
    list_filter = ['status', 'is_verified', 'is_active', 'accepted_terms', 'created_at', 'state']
    search_fields = ['user__username', 'user__email', 'full_name', 'cpf', 'phone', 'city']
    readonly_fields = [
        'total_views', 'total_books', 'total_followers',
        'created_at', 'updated_at', 'approved_at', 'rejected_at',
        'accepted_terms_at', 'terms_ip_address', 'accepted_terms_version'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Pessoais (Obrigatórias)', {
            'fields': ('full_name', 'cpf', 'birth_date', 'phone')
        }),
        ('Endereço Completo', {
            'fields': ('cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
        }),
        ('Informações Profissionais', {
            'fields': ('bio', 'literary_experience', 'writing_genres', 'photo')
        }),
        ('Documentação', {
            'fields': ('identity_document', 'cpf_document', 'proof_of_address'),
            'description': 'Documentos enviados pelo autor para validação'
        }),
        ('Redes Sociais', {
            'fields': ('website', 'twitter', 'instagram', 'facebook', 'linkedin'),
            'classes': ('collapse',)
        }),
        ('Termo de Responsabilidade', {
            'fields': ('accepted_terms', 'accepted_terms_version', 'accepted_terms_at', 'terms_ip_address'),
            'classes': ('collapse',)
        }),
        ('Status e Aprovação', {
            'fields': ('status', 'is_verified', 'is_active', 'admin_notes', 'rejection_reason'),
            'description': 'Controle de aprovação do cadastro'
        }),
        ('Estatísticas', {
            'fields': ('total_views', 'total_books', 'total_followers'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'rejected_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'reviewing': '#3498db',
            'approved': '#27ae60',
            'rejected': '#e74c3c',
            'suspended': '#95a5a6',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['approve_authors', 'reject_authors', 'set_reviewing', 'suspend_authors']

    def approve_authors(self, request, queryset):
        """Aprova autores selecionados"""
        count = 0
        for author in queryset:
            if not author.accepted_terms:
                messages.warning(request, f'{author.full_name} não aceitou os termos ainda.')
                continue
            if not author.is_adult():
                messages.error(request, f'{author.full_name} é menor de 18 anos.')
                continue
            if not author.identity_document or not author.proof_of_address:
                messages.warning(request, f'{author.full_name} está com documentos faltando.')
                continue

            author.status = 'approved'
            author.approved_at = timezone.now()
            author.is_active = True
            author.is_verified = True  # Marca como verificado ao aprovar
            author.save()
            count += 1

        if count > 0:
            self.message_user(request, f'{count} autor(es) aprovado(s) com sucesso.', messages.SUCCESS)
    approve_authors.short_description = '✅ Aprovar autores selecionados'

    def reject_authors(self, request, queryset):
        """Rejeita autores selecionados"""
        count = queryset.update(
            status='rejected',
            rejected_at=timezone.now(),
            is_active=False,
            is_verified=False
        )
        self.message_user(request, f'{count} autor(es) rejeitado(s).', messages.WARNING)
    reject_authors.short_description = '❌ Rejeitar autores selecionados'

    def set_reviewing(self, request, queryset):
        """Coloca autores em análise"""
        count = queryset.update(status='reviewing', is_active=False)
        self.message_user(request, f'{count} autor(es) colocado(s) em análise.', messages.INFO)
    set_reviewing.short_description = '🔍 Colocar em análise'

    def suspend_authors(self, request, queryset):
        """Suspende autores"""
        count = queryset.update(status='suspended', is_active=False, is_verified=False)
        self.message_user(request, f'{count} autor(es) suspenso(s).', messages.ERROR)
    suspend_authors.short_description = '🚫 Suspender autores'


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


@admin.register(BookLike)
class BookLikeAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['book__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(PublisherProfile)
class PublisherProfileAdmin(admin.ModelAdmin):
    list_display = [
        'company_name',
        'user',
        'user_type_display',
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
            'fields': ('user',),
            'description': '<strong>⚠️ ATENÇÃO:</strong> O usuário selecionado será o responsável por esta editora. '
                          'Certifique-se de que:<br>'
                          '• O usuário NÃO é um autor emergente (evite usar sua conta pessoal)<br>'
                          '• O usuário NÃO é um superusuário/admin<br>'
                          '• O usuário foi criado especificamente para esta editora'
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

    def user_type_display(self, obj):
        """Exibe o tipo de usuário vinculado"""
        user = obj.user
        badges = []

        if user.is_superuser:
            badges.append('<span style="background-color: #e74c3c; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">⚠️ SUPERUSUÁRIO</span>')

        if hasattr(user, 'emerging_author_profile'):
            badges.append('<span style="background-color: #f39c12; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">⚠️ AUTOR</span>')

        if user.is_staff:
            badges.append('<span style="background-color: #3498db; color: white; padding: 2px 8px; border-radius: 3px;">STAFF</span>')

        if not badges:
            badges.append('<span style="background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 3px;">✓ USUÁRIO COMUM</span>')

        return format_html(' '.join(badges))
    user_type_display.short_description = 'Tipo de Usuário'

    def save_model(self, request, obj, form, change):
        """Valida antes de salvar"""
        user = obj.user

        # Aviso se é superusuário
        if user.is_superuser:
            messages.warning(
                request,
                f'⚠️ ATENÇÃO: Você está vinculando a editora "{obj.company_name}" ao superusuário "{user.username}". '
                'Isso pode causar confusão. Recomenda-se criar um usuário específico para cada editora.'
            )

        # Aviso se é autor emergente
        if hasattr(user, 'emerging_author_profile'):
            messages.warning(
                request,
                f'⚠️ ATENÇÃO: O usuário "{user.username}" já é um autor emergente. '
                'Um usuário não deveria ser autor E editora ao mesmo tempo. '
                'Recomenda-se criar um usuário separado para a editora.'
            )

        super().save_model(request, obj, form, change)

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

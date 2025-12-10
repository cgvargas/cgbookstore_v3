"""
Models para a plataforma de Novos Autores
CG.BookStore v3 - Espaço para talentos emergentes
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
import os
import re


def author_photo_path(instance, filename):
    """Define o caminho para foto do autor"""
    ext = os.path.splitext(filename)[1]
    return f'new_authors/photos/{instance.user.username}_{instance.id}{ext}'


def book_cover_path(instance, filename):
    """Define o caminho para capa do livro"""
    ext = os.path.splitext(filename)[1]
    slug = slugify(instance.title)
    return f'new_authors/covers/{slug}_{instance.id}{ext}'


def chapter_file_path(instance, filename):
    """Define o caminho para arquivos de capítulos"""
    ext = os.path.splitext(filename)[1]
    return f'new_authors/chapters/{instance.book.slug}/{instance.number}_{instance.slug}{ext}'


class AuthorTermsOfService(models.Model):
    """
    Termo de Responsabilidade e Uso da Plataforma para Autores Emergentes
    """
    title = models.CharField('Título', max_length=200, default='Termo de Responsabilidade - Autores Emergentes')
    version = models.CharField('Versão', max_length=20, unique=True, help_text='Ex: 1.0, 1.1, 2.0')

    # Conteúdo do termo
    content = models.TextField(
        'Conteúdo do Termo',
        help_text='Texto completo do termo de responsabilidade em markdown ou HTML'
    )

    # Resumo dos pontos principais
    summary_points = models.JSONField(
        'Pontos Principais',
        default=list,
        help_text='Lista dos pontos principais do termo para exibição rápida'
    )

    # Controle
    is_active = models.BooleanField('Versão Ativa', default=True)
    is_current = models.BooleanField('Versão Atual', default=False, help_text='Apenas uma versão pode ser a atual')

    # Datas
    effective_date = models.DateTimeField('Data de Vigência', help_text='Data em que este termo entra em vigor')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_terms_of_service'
        verbose_name = 'Termo de Responsabilidade'
        verbose_name_plural = 'Termos de Responsabilidade'
        ordering = ['-version']

    def __str__(self):
        return f"{self.title} - Versão {self.version}"

    def save(self, *args, **kwargs):
        """Garante que apenas uma versão seja a atual"""
        if self.is_current:
            AuthorTermsOfService.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class EmergingAuthor(models.Model):
    """
    Perfil de autor emergente na plataforma
    IMPORTANTE: Requer aprovação manual do admin antes de poder publicar
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='emerging_author_profile'
    )

    # ========== INFORMAÇÕES PESSOAIS OBRIGATÓRIAS ==========
    full_name = models.CharField(
        'Nome Completo',
        max_length=200,
        blank=True,
        default='',
        help_text='Nome completo como aparecerá nas publicações (obrigatório para aprovação)'
    )
    cpf = models.CharField(
        'CPF',
        max_length=14,
        blank=True,
        default='',
        help_text='CPF para validação (formato: 000.000.000-00) - obrigatório para aprovação'
    )
    birth_date = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True,
        help_text='Você deve ter no mínimo 18 anos (obrigatório para aprovação)'
    )
    phone = models.CharField(
        'Telefone/Celular',
        max_length=20,
        blank=True,
        default='',
        help_text='Formato: (00) 00000-0000 (obrigatório para aprovação)'
    )

    # ========== ENDEREÇO ==========
    cep = models.CharField('CEP', max_length=9, blank=True, default='', help_text='Formato: 00000-000 (obrigatório para aprovação)')
    street = models.CharField('Rua/Avenida', max_length=200, blank=True, default='')
    number = models.CharField('Número', max_length=10, blank=True, default='')
    complement = models.CharField('Complemento', max_length=100, blank=True, default='')
    neighborhood = models.CharField('Bairro', max_length=100, blank=True, default='')
    city = models.CharField('Cidade', max_length=100, blank=True, default='')
    state = models.CharField('Estado', max_length=2, blank=True, default='', help_text='UF (ex: SP, RJ, MG)')

    # ========== INFORMAÇÕES PROFISSIONAIS ==========
    bio = models.TextField(
        'Biografia Literária',
        max_length=2000,
        blank=True,
        default='',
        help_text='Conte sua história como escritor, experiências e objetivos (obrigatório para aprovação)'
    )
    literary_experience = models.TextField(
        'Experiência Literária',
        max_length=1000,
        blank=True,
        default='',
        help_text='Descreva sua experiência anterior: prêmios, publicações, cursos, etc.'
    )
    writing_genres = models.JSONField(
        'Gêneros de Escrita',
        default=list,
        blank=True,
        help_text='Gêneros literários que você escreve'
    )

    photo = models.ImageField(
        'Foto do Autor',
        upload_to=author_photo_path,
        blank=True,
        null=True,
        help_text='Foto profissional (obrigatória para aprovação)'
    )

    # ========== DOCUMENTAÇÃO ==========
    identity_document = models.FileField(
        'Documento de Identidade',
        upload_to='new_authors/documents/',
        blank=True,
        null=True,
        help_text='Upload de RG ou CNH (frente e verso em PDF) - obrigatório para aprovação'
    )
    cpf_document = models.FileField(
        'Comprovante de CPF',
        upload_to='new_authors/documents/',
        help_text='Upload do CPF em PDF',
        blank=True,
        null=True
    )
    proof_of_address = models.FileField(
        'Comprovante de Residência',
        upload_to='new_authors/documents/',
        blank=True,
        null=True,
        help_text='Conta de luz, água ou telefone (últimos 3 meses) - obrigatório para aprovação'
    )

    # ========== REDES SOCIAIS E CONTATO ==========
    website = models.URLField('Website Pessoal', blank=True)
    twitter = models.CharField('Twitter/X', max_length=100, blank=True)
    instagram = models.CharField('Instagram', max_length=100, blank=True)
    facebook = models.CharField('Facebook', max_length=100, blank=True)
    linkedin = models.CharField('LinkedIn', max_length=100, blank=True)

    # ========== ESTATÍSTICAS ==========
    total_views = models.IntegerField('Total de Visualizações', default=0)
    total_books = models.IntegerField('Total de Livros', default=0)
    total_followers = models.IntegerField('Total de Seguidores', default=0)

    # ========== APROVAÇÃO E STATUS ==========
    STATUS_CHOICES = [
        ('pending', 'Pendente de Aprovação'),
        ('reviewing', 'Em Análise'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('suspended', 'Suspenso'),
    ]

    status = models.CharField(
        'Status de Aprovação',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Status do cadastro perante o admin'
    )
    is_verified = models.BooleanField('E-mail Verificado', default=False)
    is_active = models.BooleanField('Ativo', default=False)

    # Justificativa do admin
    admin_notes = models.TextField(
        'Observações do Admin',
        blank=True,
        help_text='Notas internas sobre a aprovação/rejeição'
    )
    rejection_reason = models.TextField(
        'Motivo da Rejeição',
        blank=True,
        help_text='Motivo caso o cadastro seja rejeitado'
    )

    # Datas importantes
    approved_at = models.DateTimeField('Aprovado em', null=True, blank=True)
    rejected_at = models.DateTimeField('Rejeitado em', null=True, blank=True)

    # ========== TERMO DE RESPONSABILIDADE ==========
    accepted_terms = models.BooleanField(
        'Aceito os Termos de Uso',
        default=False,
        help_text='É obrigatório aceitar os termos para continuar'
    )
    accepted_terms_version = models.ForeignKey(
        'AuthorTermsOfService',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_by_authors',
        verbose_name='Versão do Termo Aceita',
        help_text='Versão específica do termo que foi aceita'
    )
    accepted_terms_at = models.DateTimeField(
        'Termos Aceitos em',
        null=True,
        blank=True
    )
    terms_ip_address = models.GenericIPAddressField(
        'IP de Aceitação dos Termos',
        null=True,
        blank=True
    )

    # ========== METADATA ==========
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_emerging_author'
        verbose_name = 'Autor Emergente'
        verbose_name_plural = 'Autores Emergentes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user'], name='idx_emerging_author_user'),
            models.Index(fields=['-total_views'], name='idx_emerging_author_views'),
            models.Index(fields=['is_verified', 'is_active'], name='idx_emerging_author_status'),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.user.username}) - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """Atualiza datas de aprovação/rejeição"""
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
            self.is_active = True
        elif self.status == 'rejected' and not self.rejected_at:
            self.rejected_at = timezone.now()
            self.is_active = False
        elif self.status in ['pending', 'reviewing']:
            self.is_active = False

        super().save(*args, **kwargs)

    def update_statistics(self):
        """Atualiza as estatísticas do autor"""
        self.total_books = self.books.filter(status='published').count()
        self.total_views = sum(book.views_count for book in self.books.all())
        self.save()

    def can_publish(self):
        """Verifica se o autor pode publicar livros"""
        return self.status == 'approved' and self.is_active and self.accepted_terms

    def is_adult(self):
        """Verifica se o autor tem 18 anos ou mais"""
        from datetime import date
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age >= 18

    def validate_cpf(self):
        """Validação básica de CPF (apenas formato)"""
        import re
        cpf = re.sub(r'[^0-9]', '', self.cpf)
        return len(cpf) == 11


class AuthorBook(models.Model):
    """
    Livro publicado por um autor emergente
    """
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('review', 'Em Revisão'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]

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
        ('other', 'Outro'),
    ]

    # Relações
    author = models.ForeignKey(
        EmergingAuthor,
        on_delete=models.CASCADE,
        related_name='books'
    )

    # Informações básicas
    title = models.CharField('Título', max_length=200)
    slug = models.SlugField('Slug', max_length=250, unique=True, blank=True)
    subtitle = models.CharField('Subtítulo', max_length=200, blank=True)

    # Descrição e sinopse
    synopsis = models.TextField(
        'Sinopse',
        max_length=1000,
        help_text='Breve descrição do livro'
    )
    description = models.TextField(
        'Descrição Completa',
        help_text='Descrição detalhada do livro e enredo',
        blank=True,
        default=''
    )

    # Capa
    cover_image = models.ImageField(
        'Capa do Livro',
        upload_to=book_cover_path,
        help_text='Recomendado: 600x900px'
    )

    # Categorização
    genre = models.CharField('Gênero', max_length=20, choices=GENRE_CHOICES)
    tags = models.JSONField('Tags', default=list, blank=True)

    # Status e controle
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Estatísticas
    views_count = models.IntegerField('Visualizações', default=0)
    likes_count = models.IntegerField('Curtidas', default=0)
    rating_average = models.DecimalField(
        'Avaliação Média',
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    rating_count = models.IntegerField('Total de Avaliações', default=0)

    # Informações adicionais
    estimated_pages = models.IntegerField('Páginas Estimadas', default=0)
    language = models.CharField('Idioma', max_length=10, default='pt-BR')

    # Datas
    published_at = models.DateTimeField('Publicado em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_book'
        verbose_name = 'Livro de Autor Emergente'
        verbose_name_plural = 'Livros de Autores Emergentes'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['author', '-published_at'], name='idx_book_author_date'),
            models.Index(fields=['status'], name='idx_book_status'),
            models.Index(fields=['genre'], name='idx_book_genre'),
            models.Index(fields=['-rating_average'], name='idx_book_rating'),
            models.Index(fields=['-views_count'], name='idx_book_views'),
            models.Index(fields=['slug'], name='idx_book_slug'),
        ]

    def __str__(self):
        return f"{self.title} - {self.author}"

    def save(self, *args, **kwargs):
        """Gera slug automaticamente se não existir"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while AuthorBook.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Atualiza data de publicação
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Retorna a URL do livro"""
        return reverse('new_authors:book_detail', kwargs={'slug': self.slug})

    def update_rating(self):
        """Atualiza a média de avaliações"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            self.rating_average = reviews.aggregate(
                models.Avg('rating')
            )['rating__avg']
            self.rating_count = reviews.count()
        else:
            self.rating_average = 0.00
            self.rating_count = 0
        self.save()

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Chapter(models.Model):
    """
    Capítulo de um livro
    """
    book = models.ForeignKey(
        AuthorBook,
        on_delete=models.CASCADE,
        related_name='chapters'
    )

    # Informações do capítulo
    number = models.PositiveIntegerField('Número do Capítulo')
    title = models.CharField('Título', max_length=200)
    slug = models.SlugField('Slug', max_length=250, blank=True)

    # Conteúdo
    content = models.TextField(
        'Conteúdo',
        help_text='Texto completo do capítulo'
    )

    # Arquivo opcional (para upload de documentos)
    file = models.FileField(
        'Arquivo',
        upload_to=chapter_file_path,
        blank=True,
        null=True,
        help_text='PDF, DOCX ou TXT'
    )

    # Preview
    preview = models.TextField(
        'Preview',
        max_length=500,
        blank=True,
        help_text='Primeiras linhas do capítulo'
    )

    # Notas do autor
    author_notes = models.TextField(
        'Notas do Autor',
        blank=True,
        help_text='Notas ou comentários do autor sobre o capítulo'
    )

    # Controle
    is_published = models.BooleanField('Publicado', default=False)
    is_free = models.BooleanField(
        'Gratuito',
        default=True,
        help_text='Se falso, requer login para ler'
    )

    # Estatísticas
    word_count = models.IntegerField('Contagem de Palavras', default=0)
    views_count = models.IntegerField('Visualizações', default=0)

    # Datas
    published_at = models.DateTimeField('Publicado em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_chapter'
        verbose_name = 'Capítulo'
        verbose_name_plural = 'Capítulos'
        ordering = ['book', 'number']
        unique_together = ['book', 'number']
        indexes = [
            models.Index(fields=['book', 'number'], name='idx_chapter_book_num'),
            models.Index(fields=['is_published'], name='idx_chapter_published'),
        ]

    def __str__(self):
        return f"{self.book.title} - Cap. {self.number}: {self.title}"

    def save(self, *args, **kwargs):
        """Gera slug e preview automaticamente"""
        if not self.slug:
            self.slug = slugify(self.title)

        # Gera preview se não existir
        if not self.preview and self.content:
            self.preview = self.content[:500]

        # Conta palavras
        if self.content:
            self.word_count = len(self.content.split())

        # Atualiza data de publicação
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Retorna a URL do capítulo"""
        return reverse('new_authors:chapter_read', kwargs={
            'book_slug': self.book.slug,
            'chapter_number': self.number
        })

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class AuthorBookReview(models.Model):
    """
    Avaliação/Review de um livro de autor emergente
    """
    book = models.ForeignKey(
        AuthorBook,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emerging_book_reviews'
    )

    # Avaliação
    rating = models.IntegerField(
        'Avaliação',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1 a 5 estrelas'
    )

    # Review
    title = models.CharField('Título', max_length=200, blank=True)
    comment = models.TextField('Comentário', max_length=2000)

    # Interações
    helpful_count = models.IntegerField('Útil', default=0)
    report_count = models.IntegerField('Denúncias', default=0)

    # Moderação
    is_approved = models.BooleanField('Aprovado', default=True)
    is_featured = models.BooleanField('Destaque', default=False)

    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_review'
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']
        unique_together = ['book', 'user']
        indexes = [
            models.Index(fields=['book', '-created_at'], name='idx_review_book_date'),
            models.Index(fields=['user'], name='idx_review_user'),
            models.Index(fields=['is_approved', '-helpful_count'], name='idx_review_approved'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}★)"

    def save(self, *args, **kwargs):
        """Atualiza a média do livro após salvar"""
        super().save(*args, **kwargs)
        self.book.update_rating()


class BookFollower(models.Model):
    """
    Seguidores de um livro (para receber notificações de novos capítulos)
    """
    book = models.ForeignKey(
        AuthorBook,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_books'
    )

    # Preferências de notificação
    notify_new_chapter = models.BooleanField('Notificar novos capítulos', default=True)
    notify_updates = models.BooleanField('Notificar atualizações', default=True)

    # Metadata
    created_at = models.DateTimeField('Seguindo desde', auto_now_add=True)

    class Meta:
        db_table = 'new_authors_follower'
        verbose_name = 'Seguidor de Livro'
        verbose_name_plural = 'Seguidores de Livros'
        unique_together = ['book', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['book'], name='idx_follower_book'),
            models.Index(fields=['user'], name='idx_follower_user'),
        ]

    def __str__(self):
        return f"{self.user.username} segue {self.book.title}"


class BookLike(models.Model):
    """
    Curtidas de um livro
    """
    book = models.ForeignKey(
        AuthorBook,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='liked_books'
    )

    # Metadata
    created_at = models.DateTimeField('Curtido em', auto_now_add=True)

    class Meta:
        db_table = 'new_authors_book_like'
        verbose_name = 'Curtida de Livro'
        verbose_name_plural = 'Curtidas de Livros'
        unique_together = ['book', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['book'], name='idx_like_book'),
            models.Index(fields=['user'], name='idx_like_user'),
        ]

    def __str__(self):
        return f"{self.user.username} curtiu {self.book.title}"

    def save(self, *args, **kwargs):
        """Atualiza o contador de curtidas do livro ao salvar"""
        super().save(*args, **kwargs)
        self.book.likes_count = self.book.likes.count()
        self.book.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        """Atualiza o contador de curtidas do livro ao deletar"""
        book = self.book
        super().delete(*args, **kwargs)
        book.likes_count = book.likes.count()
        book.save(update_fields=['likes_count'])


class PublisherProfile(models.Model):
    """
    Perfil de editora que pode avaliar e contactar autores
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='publisher_profile'
    )

    # Informações da editora
    company_name = models.CharField('Nome da Editora', max_length=200)
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        blank=True,
        default='',
        help_text='CNPJ da editora (formato: XX.XXX.XXX/XXXX-XX)'
    )
    description = models.TextField('Descrição', max_length=1000)
    logo = models.ImageField('Logo', upload_to='new_authors/publishers/', blank=True)

    # Contato
    website = models.URLField('Website', blank=True)
    email = models.EmailField('Email de Contato')
    phone = models.CharField('Telefone', max_length=20, blank=True)

    # Aprovação
    is_verified = models.BooleanField('Verificada', default=False)
    is_active = models.BooleanField('Ativa', default=True)

    # Estatísticas
    authors_contacted = models.IntegerField('Autores Contatados', default=0)

    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_publisher'
        verbose_name = 'Editora'
        verbose_name_plural = 'Editoras'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_verified', 'is_active'], name='idx_publisher_status'),
            models.Index(fields=['cnpj'], name='idx_publisher_cnpj'),
        ]

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        """Formata CNPJ antes de salvar"""
        if self.cnpj:
            # Remove pontuação
            cnpj_clean = re.sub(r'[^\d]', '', self.cnpj)
            # Formata: XX.XXX.XXX/XXXX-XX
            if len(cnpj_clean) == 14:
                self.cnpj = f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
        super().save(*args, **kwargs)


class PublisherInterest(models.Model):
    """
    Registro de interesse de uma editora em um autor/livro
    """
    publisher = models.ForeignKey(
        PublisherProfile,
        on_delete=models.CASCADE,
        related_name='interests'
    )
    book = models.ForeignKey(
        AuthorBook,
        on_delete=models.CASCADE,
        related_name='publisher_interests'
    )

    # Interesse
    message = models.TextField(
        'Mensagem',
        max_length=1000,
        help_text='Mensagem da editora para o autor'
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=[
            ('pending', 'Pendente'),
            ('contacted', 'Contatado'),
            ('negotiating', 'Negociando'),
            ('closed', 'Finalizado'),
            ('rejected', 'Rejeitado'),
        ],
        default='pending'
    )

    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'new_authors_publisher_interest'
        verbose_name = 'Interesse de Editora'
        verbose_name_plural = 'Interesses de Editoras'
        ordering = ['-created_at']
        unique_together = ['publisher', 'book']
        indexes = [
            models.Index(fields=['publisher', '-created_at'], name='idx_interest_publisher'),
            models.Index(fields=['book', '-created_at'], name='idx_interest_book'),
            models.Index(fields=['status'], name='idx_interest_status'),
        ]

    def __str__(self):
        return f"{self.publisher.company_name} → {self.book.title}"

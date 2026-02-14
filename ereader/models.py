from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class EBook(models.Model):
    """Modelo para armazenar metadados de e-books."""
    
    SOURCE_CHOICES = [
        ('gutenberg', 'Project Gutenberg'),
        ('openlibrary', 'Open Library'),
        ('upload', 'Upload Manual'),
        ('archive', 'Internet Archive'),
    ]
    
    LANGUAGE_CHOICES = [
        ('pt', 'Português'),
        ('en', 'English'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
        ('other', 'Outro'),
    ]
    
    title = models.CharField('Título', max_length=500)
    author = models.CharField('Autor', max_length=300)
    description = models.TextField('Descrição', blank=True)
    
    # Arquivos e imagens
    cover_image = models.URLField('URL da Capa', blank=True)
    epub_file = models.FileField('Arquivo EPUB', upload_to='ebooks/', blank=True, null=True)
    epub_url = models.URLField('URL do EPUB', blank=True, help_text='Para livros externos')
    
    # Metadados
    source = models.CharField('Fonte', max_length=20, choices=SOURCE_CHOICES, default='gutenberg')
    external_id = models.CharField('ID Externo', max_length=100, blank=True, 
                                    help_text='ID na fonte externa (ex: Gutenberg ID)')
    language = models.CharField('Idioma', max_length=10, choices=LANGUAGE_CHOICES, default='pt')
    
    # Informações adicionais
    publisher = models.CharField('Editora', max_length=200, blank=True)
    publish_year = models.PositiveIntegerField('Ano de Publicação', null=True, blank=True)
    subjects = models.JSONField('Assuntos/Categorias', default=list, blank=True)
    
    # Status
    is_public_domain = models.BooleanField('Domínio Público', default=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    # Estatísticas
    view_count = models.PositiveIntegerField('Visualizações', default=0)
    read_count = models.PositiveIntegerField('Leituras Completas', default=0)
    
    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'E-Book'
        verbose_name_plural = 'E-Books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', 'external_id']),
            models.Index(fields=['language']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author}"
    
    def get_epub_url(self):
        """Retorna URL do EPUB (arquivo local ou externo)."""
        # 1. Prioridade para arquivo local
        if self.epub_file:
            return self.epub_file.url
        
        # 2. Se tiver URL explícita, usa ela
        if self.epub_url:
            return self.epub_url
        
        # 3. Para livros do Gutenberg, construir URL automaticamente
        if self.source == 'gutenberg' and self.external_id:
            # URL padrão do Project Gutenberg para EPUB
            # Formato: https://www.gutenberg.org/ebooks/{id}.epub.images
            return f'https://www.gutenberg.org/ebooks/{self.external_id}.epub.images'
        
        # 4. Para livros do Internet Archive, construir URL
        if self.source == 'archive' and self.external_id:
            # Formato: https://archive.org/download/{id}/{id}.epub
            return f'https://archive.org/download/{self.external_id}/{self.external_id}.epub'
        
        return ''


class UserLibrary(models.Model):
    """Biblioteca pessoal do usuário - livros salvos para leitura."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ereader_library')
    ebook = models.ForeignKey(EBook, on_delete=models.CASCADE, related_name='in_libraries')
    added_at = models.DateTimeField('Adicionado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Biblioteca do Usuário'
        verbose_name_plural = 'Bibliotecas dos Usuários'
        unique_together = ['user', 'ebook']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title}"


class UserBookProgress(models.Model):
    """Progresso de leitura do usuário em um livro."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ereader_progress')
    ebook = models.ForeignKey(EBook, on_delete=models.CASCADE, related_name='user_progress')
    
    # Posição no livro (CFI = Canonical Fragment Identifier do EPUB)
    current_cfi = models.CharField('CFI Atual', max_length=500, blank=True,
                                   help_text='Identificador de posição do epub.js')
    current_chapter = models.PositiveIntegerField('Capítulo Atual', default=0)
    
    # Progresso percentual
    percentage = models.DecimalField('Progresso (%)', max_digits=5, decimal_places=2, default=0)
    
    # Tempo de leitura
    total_reading_time = models.PositiveIntegerField('Tempo de Leitura (minutos)', default=0)
    last_session_duration = models.PositiveIntegerField('Última Sessão (minutos)', default=0)
    
    # Status
    is_finished = models.BooleanField('Finalizado', default=False)
    finished_at = models.DateTimeField('Finalizado em', null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField('Iniciado em', auto_now_add=True)
    last_read = models.DateTimeField('Última Leitura', auto_now=True)
    
    class Meta:
        verbose_name = 'Progresso de Leitura'
        verbose_name_plural = 'Progressos de Leitura'
        unique_together = ['user', 'ebook']
        ordering = ['-last_read']
    
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title} ({self.percentage}%)"
    
    def mark_as_finished(self):
        """Marca o livro como finalizado."""
        self.is_finished = True
        self.finished_at = timezone.now()
        self.percentage = 100
        self.save()
        # Incrementar contador de leituras do ebook
        self.ebook.read_count += 1
        self.ebook.save(update_fields=['read_count'])


class Bookmark(models.Model):
    """Marcadores de página salvos pelo usuário."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ereader_bookmarks')
    ebook = models.ForeignKey(EBook, on_delete=models.CASCADE, related_name='bookmarks')
    
    cfi = models.CharField('CFI', max_length=500, help_text='Posição do marcador')
    title = models.CharField('Título', max_length=200, blank=True,
                             help_text='Nome personalizado para o marcador')
    chapter_title = models.CharField('Título do Capítulo', max_length=300, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Marcador'
        verbose_name_plural = 'Marcadores'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title}: {self.title or 'Sem nome'}"


class Highlight(models.Model):
    """Destaques de texto feitos pelo usuário."""
    
    COLOR_CHOICES = [
        ('yellow', 'Amarelo'),
        ('green', 'Verde'),
        ('blue', 'Azul'),
        ('pink', 'Rosa'),
        ('orange', 'Laranja'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ereader_highlights')
    ebook = models.ForeignKey(EBook, on_delete=models.CASCADE, related_name='highlights')
    
    cfi_range = models.CharField('CFI Range', max_length=1000,
                                  help_text='Intervalo de texto destacado')
    text = models.TextField('Texto Destacado')
    color = models.CharField('Cor', max_length=20, choices=COLOR_CHOICES, default='yellow')
    
    chapter_title = models.CharField('Título do Capítulo', max_length=300, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Destaque'
        verbose_name_plural = 'Destaques'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title}: {self.text[:50]}..."


class ReadingNote(models.Model):
    """Notas/anotações feitas durante a leitura."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ereader_notes')
    ebook = models.ForeignKey(EBook, on_delete=models.CASCADE, related_name='reading_notes')
    
    cfi = models.CharField('CFI', max_length=500,
                           help_text='Posição da nota no livro')
    note_text = models.TextField('Nota')
    
    # Opcional: vincular a um destaque
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='notes')
    
    chapter_title = models.CharField('Título do Capítulo', max_length=300, blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Nota de Leitura'
        verbose_name_plural = 'Notas de Leitura'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title}: {self.note_text[:50]}..."


class ReaderSettings(models.Model):
    """Configurações personalizadas do leitor para cada usuário."""
    
    THEME_CHOICES = [
        ('amber', 'Âmbar (Vintage)'),
        ('green', 'Verde Fósforo'),
        ('sepia', 'Sépia'),
        ('light', 'Claro'),
        ('dark', 'Escuro'),
    ]
    
    FONT_CHOICES = [
        ('serif', 'Serif (Clássico)'),
        ('sans', 'Sans-serif (Moderno)'),
        ('mono', 'Monospace (Console)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ereader_settings')
    
    # Aparência
    theme = models.CharField('Tema', max_length=20, choices=THEME_CHOICES, default='amber')
    font_family = models.CharField('Fonte', max_length=20, choices=FONT_CHOICES, default='serif')
    font_size = models.PositiveIntegerField('Tamanho da Fonte', default=18)
    line_height = models.DecimalField('Espaçamento de Linha', max_digits=3, decimal_places=1, default=1.6)
    
    # Efeitos visuais
    scanlines_enabled = models.BooleanField('Scanlines', default=True)
    crt_curvature = models.BooleanField('Curvatura CRT', default=True)
    screen_glow = models.BooleanField('Brilho da Tela', default=True)
    
    # Som
    sound_effects = models.BooleanField('Efeitos Sonoros', default=True)
    
    # Comportamento
    auto_save_progress = models.BooleanField('Salvar Progresso Automaticamente', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Configurações do Leitor'
        verbose_name_plural = 'Configurações dos Leitores'
    
    def __str__(self):
        return f"Configurações de {self.user.username}"

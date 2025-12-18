# core/models/featured_author_settings.py
"""
Model para configurações de Autor em Destaque.
Permite personalizar a seção na home e página dedicada via Admin.
"""

from django.db import models
from django.core.exceptions import ValidationError


class FeaturedAuthorSettings(models.Model):
    """
    Configurações para seção de autor em destaque na home.
    Padrão Singleton: apenas um registro ativo por vez.
    """
    
    # Autor vinculado
    author = models.ForeignKey(
        'core.Author',
        on_delete=models.CASCADE,
        related_name='featured_settings',
        verbose_name='Autor',
        help_text='Selecione o autor em destaque'
    )
    
    # Controle de ativação
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Se marcado, a seção será exibida na home'
    )
    
    # === SEÇÃO NA HOME ===
    home_title = models.CharField(
        max_length=100,
        default='Mundo de Tolkien',
        verbose_name='Título na Home',
        help_text='Título principal da seção (ex: "Mundo de Tolkien")'
    )
    
    home_subtitle = models.CharField(
        max_length=100,
        default='Explore o Mundo de',
        verbose_name='Subtítulo',
        help_text='Texto acima do título (ex: "Explore o Mundo de")'
    )
    
    home_description = models.TextField(
        default='Descubra a Terra-média através das obras do mestre da fantasia',
        verbose_name='Descrição Curta',
        help_text='Descrição exibida na seção da home'
    )
    
    home_banner_image = models.ImageField(
        upload_to='featured_authors/banners/',
        blank=True,
        null=True,
        verbose_name='Banner da Seção',
        help_text='Imagem de fundo da seção (recomendado: 1920x600px)'
    )
    
    home_button_text = models.CharField(
        max_length=50,
        default='Explorar Mundo de Tolkien',
        verbose_name='Texto do Botão',
        help_text='Texto exibido no botão de ação'
    )
    
    home_button_icon = models.CharField(
        max_length=50,
        default='fa-compass',
        verbose_name='Ícone do Botão',
        help_text='Classe Font Awesome (ex: fa-compass, fa-book)'
    )
    
    # === PÁGINA DEDICADA ===
    page_title = models.CharField(
        max_length=200,
        default='Explore o Mundo de J.R.R. Tolkien',
        verbose_name='Título da Página',
        help_text='Título exibido na página dedicada'
    )
    
    page_description = models.TextField(
        default='Mergulhe nas obras do mestre da fantasia que criou a Terra-média e encantou gerações de leitores.',
        verbose_name='Descrição da Página',
        help_text='Descrição longa exibida na página'
    )
    
    page_meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name='Meta Title (SEO)',
        help_text='Título para SEO (máx 70 caracteres)'
    )
    
    page_meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='Meta Description (SEO)',
        help_text='Descrição para SEO (máx 160 caracteres)'
    )
    
    # Estatísticas customizadas
    stat_badge_1 = models.CharField(
        max_length=30,
        default='Épicos',
        blank=True,
        verbose_name='Badge 1',
        help_text='Primeiro badge/rótulo de estatística'
    )
    
    stat_badge_2 = models.CharField(
        max_length=30,
        default='Lendários',
        blank=True,
        verbose_name='Badge 2',
        help_text='Segundo badge/rótulo de estatística'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Autor em Destaque'
        verbose_name_plural = 'Autores em Destaque'
        ordering = ['-is_active', '-updated_at']
    
    def __str__(self):
        status = '✓' if self.is_active else '✗'
        return f'{status} {self.author.name} - {self.home_title}'
    
    def clean(self):
        """Validação: apenas um registro ativo por vez"""
        if self.is_active:
            existing = FeaturedAuthorSettings.objects.filter(is_active=True)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    'Já existe um autor em destaque ativo. '
                    'Desative o atual antes de ativar outro.'
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active(cls):
        """Retorna a configuração ativa ou None"""
        return cls.objects.filter(is_active=True).select_related('author').first()
    
    def get_banner_url(self):
        """Retorna URL do banner ou None"""
        if self.home_banner_image:
            return self.home_banner_image.url
        return None

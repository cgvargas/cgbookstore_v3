# core/models/institutional_source.py
"""
Modelo para registro e reutilização de fontes e domínios institucionais oficiais
de editoras, autores e instituições culturais (Fase 3A.1).

DIRETRIZ CENTRAL:
- Esta estrutura NÃO representa titularidade jurídica ou autorização de uso.
- Serve apenas para reconhecer e reutilizar:
  "Este é o domínio institucional oficial utilizado pela editora/instituição."
- Evita consultas web repetitivas e armazena referências operacionais de termos de uso.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class InstitutionalSource(models.Model):
    """
    Registro de domínio institucional oficial associado a uma editora ou instituição.
    Permite busca controlada e reutilização segura de URLs de termos de uso e páginas oficiais.
    """

    INSTITUTION_TYPE_CHOICES = [
        ('publisher', '📚 Editora / Selo Editorial'),
        ('author_estate', '🖋️ Espólio / Fundação de Autor'),
        ('cultural_institution', '🏛️ Museu / Arquivo / Instituição Cultural'),
        ('academic', '🎓 Editora Universitária / Acadêmica'),
        ('agency', '🏢 Agência Literária / Representação'),
        ('other', '🌐 Outro'),
    ]

    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Nome da Instituição / Editora",
        help_text="Nome canônico da editora (ex: 'HarperCollins Brasil', 'Companhia das Letras')."
    )

    domain = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Domínio Oficial",
        help_text="Domínio limpo sem protocolo ou caminhos (ex: 'harpercollins.com.br')."
    )

    institution_type = models.CharField(
        max_length=30,
        choices=INSTITUTION_TYPE_CHOICES,
        default='publisher',
        verbose_name="Tipo da Instituição"
    )

    main_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL Principal / Site Oficial",
        help_text="URL completa do site institucional oficial (ex: 'https://harpercollins.com.br')."
    )

    terms_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL de Termos de Uso",
        help_text="Página institucional oficial de Termos de Uso / Condições Gerais."
    )

    permissions_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL de Permissões / Direitos / Imprensa",
        help_text="Página institucional de Direitos, Permissions, Media ou Contato de Licenciamento."
    )

    terms_summary = models.TextField(
        blank=True,
        verbose_name="Resumo Operacional dos Termos",
        help_text="Resumo factual e operacional curto das diretrizes de conteúdo identificadas (sem parecer jurídico)."
    )

    terms_content_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Hash do Conteúdo dos Termos",
        help_text="Hash SHA-256 do trecho analisado para detecção de alterações na página institucional."
    )

    terms_retrieved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Consulta dos Termos"
    )

    is_verified = models.BooleanField(
        default=True,
        verbose_name="Domínio Verificado",
        help_text="Indica se o domínio institucional foi validado (por curadoria ou confirmação administrativa)."
    )

    verified_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Validação"
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_institutional_sources',
        verbose_name="Validado por"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observações Internas"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Fonte Institucional Oficial"
        verbose_name_plural = "Fontes Institucionais Oficiais"
        ordering = ['name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.name} ({self.domain})"

    @property
    def is_terms_recent(self) -> bool:
        """
        Informa se os termos foram coletados nos últimos 30 dias.
        """
        if not self.terms_url or not self.terms_retrieved_at:
            return False
        return (timezone.now() - self.terms_retrieved_at) < timedelta(days=30)

# core/models/image_rights.py
"""
Modelo para Gestão Corporativa de Direitos Autorais, Procedência e Licenciamento de Imagens.
Entidade centralizada vinculada via GenericForeignKey a qualquer campo de imagem da plataforma.
"""

import hashlib
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ImageRightsRecord(models.Model):
    """
    Entidade central de direitos autorais, procedência e governança de ativos visuais.
    Relaciona-se individualmente com qualquer campo de imagem de qualquer modelo via GenericForeignKey.
    """

    LICENSE_CHOICES = [
        ('own', '🏠 Própria / CG.BookStore'),
        ('licensed', '📄 Licenciada / Comprada (Banco de Imagens/Estúdio)'),
        ('cc', '🔀 Creative Commons'),
        ('public_domain', '🌐 Domínio Público'),
        ('publisher', '📚 Cortesia da Editora / Divulgação'),
        ('amazon', '🛒 Amazon Brasil'),
        ('google_books', '🔍 Google Books'),
        ('open_library', '📖 Open Library'),
        ('wikimedia', '🏛️ Wikimedia Commons'),
        ('other', '📌 Outra'),
    ]

    # Relacionamento Genérico (compatível com BigAutoField via PositiveBigIntegerField)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Tipo de Conteúdo"
    )
    object_id = models.PositiveBigIntegerField(
        db_index=True,
        verbose_name="ID do Objeto Relacionado"
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Identificação exata do campo de imagem (validado no Admin)
    image_field_name = models.CharField(
        max_length=100,
        verbose_name="Campo da Imagem",
        help_text="Nome exato do campo de imagem no modelo (ex: hero_banner_image, cover_image)."
    )

    # Identificação do Arquivo e Checksum (Detecção de Troca de Imagem)
    image_file_name = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Caminho/Nome do Arquivo Auditado"
    )
    image_checksum = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Checksum SHA-256 da Imagem"
    )

    # Atribuição TASL (Title, Author, Source, License)
    work_title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Título da Obra Visual",
        help_text="Título original ou nome dado à ilustração/foto (necessário para atribuição TASL)."
    )
    credit_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Autor / Criador / Detentor dos Direitos",
        help_text="Nome do artista, fotógrafo, ilustrador ou empresa responsável."
    )
    source_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="URL da Fonte Original",
        help_text="Link oficial da publicação ou portfólio de onde a imagem foi extraída."
    )

    # Regime Jurídico e Origem (Independentes)
    license_type = models.CharField(
        max_length=30,
        choices=LICENSE_CHOICES,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Regime de Licença",
        help_text="Tipo de licença jurídica. Deixe em branco se a licença ainda não foi auditada."
    )
    license_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="URL Oficial da Licença",
        help_text="Link oficial dos termos da licença (obrigatório/recomendado para Creative Commons)."
    )
    is_ai_generated = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Gerada por Inteligência Artificial?",
        help_text="Marque se a imagem foi sintetizada por ferramenta de IA (Midjourney, DALL-E, etc.)."
    )

    # Documentação Privada e Observações Internas
    usage_notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Observações Internas e Restrições de Uso",
        help_text="Uso interno: detalhes de autorização, cortes, e-mails de autorização."
    )
    permission_document = models.FileField(
        upload_to='private_copyright_docs/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Documento Comprobatório / Contrato / Autorização",
        help_text="Documento comprobatório privado (Acessível via View autenticada de Admin)."
    )

    # Auditoria e Responsabilidade
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Cadastrado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável pelo Cadastro"
    )

    class Meta:
        verbose_name = "Registro de Direitos Autorais de Imagem"
        verbose_name_plural = "Registros de Direitos Autorais de Imagens"
        unique_together = [('content_type', 'object_id', 'image_field_name')]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['license_type', 'is_ai_generated']),
        ]

    def __str__(self):
        license_label = dict(self.LICENSE_CHOICES).get(self.license_type, 'Sem licença informada')
        return f"{self.content_type.model}#{self.object_id} [{self.image_field_name}] - {license_label}"

    @staticmethod
    def calculate_file_checksum(file_field):
        """Gera SHA-256 de um campo FileField / ImageField se o arquivo existir."""
        if not file_field:
            return ''
        try:
            hasher = hashlib.sha256()
            file_field.open('rb')
            for chunk in file_field.chunks():
                hasher.update(chunk)
            file_field.close()
            return hasher.hexdigest()
        except Exception:
            return ''

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

    AUDIT_STATUS_CHOICES = [
        ('not_audited', '⚪ Não auditada'),
        ('under_review', '🔵 Em análise'),
        ('regularized', '🟢 Regularizada'),
        ('pending', '🟡 Pendente de documentação'),
        ('contested', '🔴 Contestada'),
        ('restricted', '⛔ Uso Restrito / Suspenso'),
    ]

    LICENSE_CHOICES = [
        ('own', '🏠 Própria / CG.BookStore (Criação Interna)'),
        ('licensed', '📄 Licenciada / Comprada (Banco de Imagens / Contrato)'),
        ('cc', '🔀 Creative Commons (Licença Aberta)'),
        ('public_domain', '🌐 Domínio Público (Obra Livre)'),
        ('publisher', '📚 Origem: Editora / Divulgação (Procedência Histórica)'),
        ('amazon', '🛒 Origem: Amazon Brasil (Procedência Técnica)'),
        ('google_books', '🔍 Origem: Google Books (Procedência Técnica)'),
        ('open_library', '📖 Origem: Open Library (Procedência Técnica)'),
        ('project_gutenberg', '📜 Origem: Project Gutenberg (Procedência Técnica)'),
        ('wikimedia', '🏛️ Origem: Wikimedia Commons (Procedência Técnica)'),
        ('other', '📌 Outra Licença / Procedência'),
    ]

    PROVENANCE_PROVIDER_CHOICES = [
        ('google_books', '🔍 Google Books API'),
        ('open_library', '📖 Open Library'),
        ('project_gutenberg', '📜 Project Gutenberg'),
        ('unsplash', '📷 Unsplash API'),
        ('wikimedia', '🏛️ Wikimedia Commons'),
        ('publisher', '📚 Editora / Material de Divulgação'),
        ('amazon', '🛒 Amazon (Afiliados / Referência Técnica)'),
        ('external_api', '🌐 Outra API Externa'),
        ('internal_ai', '🤖 IA Interna (Geração Própria)'),
        ('partner', '🤝 Parceiro Institucional'),
        ('other', '📌 Outro Provedor Técnico'),
    ]

    PURPOSE_CHOICES = [
        ('review_debate', '💬 Resenha & Debate Literário'),
        ('affiliate_promotion', '🛒 Divulgação & Afiliado Amazon'),
        ('author_bio', '👤 Perfil & Biografia de Autor'),
        ('event_publicity', '📅 Divulgação Gratuita de Evento'),
        ('adaptation_info', '🎬 Adaptação Literária'),
        ('institutional', '🎨 Identidade Visual & Layout'),
        ('other', '📌 Outra'),
    ]

    LEGAL_BASIS_CHOICES = [
        ('fair_use_art46', '⚖️ Limitação legal analisada — Lei nº 9.610/98, Art. 46'),
        ('express_consent', '📜 Autorização Expressa da Editora/Autor'),
        ('amazon_affiliate_terms', '🛒 Termos do Programa de Afiliados Amazon'),
        ('public_domain', '🌐 Domínio Público'),
        ('creative_commons', '🔀 Licença Creative Commons'),
        ('own_production', '🏠 Produção Própria / Interna'),
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

    # Enquadramento e Finalidade do Uso (Proteção Jurídica)
    usage_purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Finalidade do Uso",
        help_text="Propósito do uso da imagem na aplicação (ex: resenha/debate, indicação de compra)."
    )
    legal_basis = models.CharField(
        max_length=30,
        choices=LEGAL_BASIS_CHOICES,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Fundamento Jurídico",
        help_text="Enquadramento legal para registro de conformidade (ex: Lei nº 9.610/98, Art. 46, Termos de Afiliados)."
    )

    # Dimensões e Especificações Técnicas (Resolução Proporcional)
    display_dimensions = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="Dimensões de Exibição / Resolução",
        help_text="Dimensões auditadas do arquivo ou formato na interface (ex: 400x600px - Card Preview)."
    )
    image_width_px = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Largura (px)"
    )
    image_height_px = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Altura (px)"
    )
    file_size_kb = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Tamanho do Arquivo (KB)"
    )

    # Atribuição Estruturada, Autoria e Titularidade de Direitos
    work_title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Título da Obra Visual",
        help_text="Título original ou nome dado à ilustração/foto (necessário para atribuição TASL)."
    )
    creator_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Criador / Autor da Imagem",
        help_text="Nome da pessoa física ou artista que efetivamente produziu a obra visual (ex: fotógrafo, ilustrador, designer)."
    )
    rights_holder_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Titular dos Direitos",
        help_text="Pessoa física ou jurídica detentora dos direitos patrimoniais da imagem, quando confirmada."
    )
    licensor_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Licenciante / Entidade Administradora",
        help_text="Entidade, banco de imagens, agência ou distribuidora que concede ou administra a licença de uso da imagem."
    )
    credit_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Crédito Legado / Atribuição Geral",
        help_text="Campo de compatibilidade histórica para créditos gerais não estruturados."
    )
    source_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Fonte Original da Imagem",
        help_text="Indica onde a imagem foi encontrada ou obtida. A existência de uma fonte não representa, por si só, autorização de uso."
    )

    # Estado de Auditoria e Governança Administrativa
    audit_status = models.CharField(
        max_length=30,
        choices=AUDIT_STATUS_CHOICES,
        default='not_audited',
        blank=True,
        db_index=True,
        verbose_name="Status de Auditoria e Governança",
        help_text=(
            "Conclusão administrativa da auditoria documental do ativo visual. "
            "Registros novos ou não revisados iniciam como '⚪ Não auditada'."
        )
    )

    # Controle de Exibição Pública e Suspensão Preventiva (Independente do audit_status)
    public_display_allowed = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Exibição Pública Permitida?",
        help_text=(
            "Determina administrativamente se a imagem pode ser exibida publicamente na plataforma. "
            "É independente de audit_status: caso desmarcado ou em suspensão preventiva por contestação, "
            "a exibição pública é bloqueada sem apagar o arquivo original nem o histórico."
        )
    )

    # Regime Jurídico e Origem (Independentes)
    license_type = models.CharField(
        max_length=30,
        choices=LICENSE_CHOICES,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Regime de Licença / Procedência Histórica",
        help_text=(
            "Regime jurídico de utilização da imagem. "
            "Atenção: opções de catálogo/plataforma (Amazon, Google Books, etc.) indicam apenas "
            "procedência técnica histórica e não autorizam o uso de forma automática."
        )
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

    # Proveniência e Rastreabilidade Técnica (Independentes de Licença e Fundamento Jurídico)
    provenance_provider = models.CharField(
        max_length=50,
        choices=PROVENANCE_PROVIDER_CHOICES,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Provedor Técnico de Proveniência",
        help_text="Identifica a fonte/serviço externo de onde o arquivo ou referência foi obtido (ex: google_books, open_library, project_gutenberg, unsplash, wikimedia)."
    )
    provenance_method = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Método de Importação",
        help_text="Canal técnico de aquisição (ex: api_download, api_reference, rss_sync, manual_import)."
    )
    provenance_imported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data/Hora da Importação Técnica",
        help_text="Momento em que o ativo visual foi importado do provedor externo."
    )
    provider_asset_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        db_index=True,
        verbose_name="Identificador Externo do Ativo",
        help_text="ID do ativo no catálogo da fonte externa (ex: Google Book ID, OpenLibrary Work ID, Unsplash Photo ID)."
    )
    is_auto_imported = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Importado Automaticamente?",
        help_text="Indica se os dados visuais e de proveniência nasceram através de rotinas e integrações automáticas."
    )
    provenance_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados Seguros de Proveniência",
        help_text="Snapshot estruturado de metadados técnicos seguros fornecidos pela API/fonte (sem tokens, dados pessoais ou headers)."
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
            models.Index(fields=['usage_purpose', 'legal_basis']),
            models.Index(fields=['audit_status']),
            models.Index(fields=['public_display_allowed']),
            models.Index(fields=['provenance_provider', 'is_auto_imported']),
        ]

    @property
    def can_display_publicly(self):
        """
        Determina de forma centralizada e segura se o ativo visual pode ser exibido publicamente.
        Critérios cumulativos:
        1. public_display_allowed deve ser True.
        2. audit_status não pode ser 'restricted'.
        3. Não pode haver ocorrência de contestação ativa que imponha bloqueio ('temporarily_suspended' ou 'resolved_removed').
        """
        if not self.public_display_allowed:
            return False
        if self.audit_status == 'restricted':
            return False
        if self.pk:
            has_blocking_takedown = self.takedown_requests.filter(
                status__in=['temporarily_suspended', 'resolved_removed']
            ).exists()
            if has_blocking_takedown:
                return False
        return True

    @property
    def display_author(self):
        """Retorna o criador/autor preferencial ou o crédito legado como fallback."""
        return self.creator_name.strip() if self.creator_name else self.credit_name.strip()

    def save(self, *args, **kwargs):
        if not self.audit_status:
            self.audit_status = 'not_audited'
        super().save(*args, **kwargs)

    def __str__(self):
        license_label = dict(self.LICENSE_CHOICES).get(self.license_type, 'Sem licença informada')
        return f"{self.content_type.model}#{self.object_id} [{self.image_field_name}] - {license_label}"

    @staticmethod
    def calculate_file_checksum(file_field):
        """
        Gera SHA-256 de um campo FileField / ImageField utilizando a abstração de storage do Django.
        Lê em blocos (chunks) e garante o fechamento do stream em try...finally.
        Funciona de forma independente do filesystem local (S3, GCS, Supabase, FileSystemStorage).
        """
        if not file_field or not getattr(file_field, 'name', None):
            return ''
        
        file_handle = None
        try:
            hasher = hashlib.sha256()
            file_handle = file_field.open('rb')
            if hasattr(file_field, 'chunks'):
                for chunk in file_field.chunks(chunk_size=64 * 1024):
                    hasher.update(chunk)
            else:
                while True:
                    chunk = file_handle.read(64 * 1024)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ''
        finally:
            if file_handle and hasattr(file_handle, 'close'):
                try:
                    file_handle.close()
                except Exception:
                    pass
            elif hasattr(file_field, 'close'):
                try:
                    file_field.close()
                except Exception:
                    pass

    @staticmethod
    def extract_file_metadata(file_field):
        """
        Extrai checksum, largura, altura e tamanho em KB do arquivo de imagem.
        Utiliza puramente a abstração de streams de storage do Django sem supor a existência de .path físico.
        Garante o fechamento de streams e tratamento seguro de exceções de I/O e decodificação.
        """
        if not file_field or not getattr(file_field, 'name', None):
            return {'checksum': '', 'width': None, 'height': None, 'size_kb': None}
        
        checksum = ImageRightsRecord.calculate_file_checksum(file_field)
        width, height, size_kb = None, None, None
        
        # 1. Tamanho do arquivo via API do storage/FieldFile
        try:
            if hasattr(file_field, 'size') and isinstance(file_field.size, (int, float)):
                size_kb = round(file_field.size / 1024.0, 2)
            elif hasattr(file_field, 'storage') and hasattr(file_field.storage, 'size'):
                size_bytes = file_field.storage.size(file_field.name)
                if size_bytes and isinstance(size_bytes, (int, float)):
                    size_kb = round(size_bytes / 1024.0, 2)
        except Exception:
            pass

        # 2. Dimensões da imagem via Pillow através do stream de bytes
        file_handle = None
        img = None
        try:
            from PIL import Image
            file_handle = file_field.open('rb')
            img = Image.open(file_handle)
            width, height = img.size
        except Exception:
            pass
        finally:
            if img and hasattr(img, 'close'):
                try:
                    img.close()
                except Exception:
                    pass
            if file_handle and hasattr(file_handle, 'close'):
                try:
                    file_handle.close()
                except Exception:
                    pass
            elif hasattr(file_field, 'close'):
                try:
                    file_field.close()
                except Exception:
                    pass

        return {
            'checksum': checksum,
            'width': width,
            'height': height,
            'size_kb': size_kb
        }


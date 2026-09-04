# core/models/copyright_takedown.py
"""
Modelo para Gestão de Notificações, Contestações, Takedown e Suspensão Preventiva de Ativos Visuais.
Integrado diretamente ao ImageRightsRecord da CG.BookStore.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class CopyrightTakedownRequest(models.Model):
    """
    Registro administrativo formal de solicitação de takedown, notificação ou contestação
    de direitos autorais vinculada a um ImageRightsRecord específico.
    """

    STATUS_CHOICES = [
        ('received', '📥 Recebida'),
        ('under_review', '🔍 Em análise'),
        ('awaiting_information', '🟡 Aguardando informações'),
        ('temporarily_suspended', '⛔ Imagem suspensa preventivamente'),
        ('resolved_keep', '🟢 Resolvida — uso mantido'),
        ('resolved_removed', '🔴 Resolvida — imagem retirada'),
        ('rejected', '⚪ Reclamação rejeitada / não procedente'),
    ]

    CLAIMANT_ROLE_CHOICES = [
        ('rights_holder', 'Titular dos Direitos Patrimoniais'),
        ('authorized_representative', 'Representante / Procurador Autorizado'),
        ('creator_author', 'Autor / Criador da Obra Visual'),
        ('publisher_licensor', 'Editora / Agência Licenciante'),
        ('third_party', 'Terceiro Interessado'),
        ('unknown', 'Não Informado / Desconhecido'),
        ('other', 'Outro'),
    ]

    # Vínculo com o registro de direitos autorais contestado
    image_rights_record = models.ForeignKey(
        'core.ImageRightsRecord',
        on_delete=models.PROTECT,
        related_name='takedown_requests',
        verbose_name="Registro de Direitos Autorais Contestado",
        help_text="Ativo visual objeto da notificação ou contestação."
    )

    # Estado do fluxo da ocorrência
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='received',
        db_index=True,
        verbose_name="Status da Contestação",
        help_text="Estado atual do tratamento administrativo da ocorrência."
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Data/Hora de Recebimento",
        help_text="Momento em que a notificação ou reclamação foi recebida pela plataforma."
    )

    # Dados de Identificação do Reclamante
    claimant_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Nome do Reclamante",
        help_text="Nome da pessoa física ou contato responsável pela contestação."
    )
    claimant_email = models.EmailField(
        blank=True,
        default='',
        verbose_name="E-mail de Contato",
        help_text="E-mail utilizado para comunicações formais sobre o caso."
    )
    claimant_organization = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Organização / Editora / Escritório",
        help_text="Empresa, escritório jurídico, agência ou editora representada, se houver."
    )
    claimant_role = models.CharField(
        max_length=40,
        choices=CLAIMANT_ROLE_CHOICES,
        default='rights_holder',
        blank=True,
        verbose_name="Papel Declarado do Reclamante"
    )

    # Fundamentos e Descrição da Contestação
    claim_description = models.TextField(
        verbose_name="Descrição da Reclamação",
        help_text="Resumo detalhado dos fatos e motivos alegados pelo reclamante."
    )
    claimed_rights_basis = models.TextField(
        blank=True,
        default='',
        verbose_name="Fundamento Jurídico Alegado",
        help_text="Base legal ou contratual apontada pelo reclamante (ex: titularidade de copyright, ausência de licença)."
    )
    source_notice_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="URL da Notificação / Referência Original",
        help_text="Link oficial da obra original, portfólio do autor ou notificação externa."
    )

    # Documentação Probatória e Observações Privadas
    evidence_document = models.FileField(
        upload_to='private_takedown_docs/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Documento / Notificação Comprobatória (Privado)",
        help_text="Arquivo restrito a administradores (notificação extrajudicial, procuração, certidão de registro)."
    )
    internal_notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Notas Administrativas Privadas",
        help_text="Anotações internas sobre a análise, parecer jurídico e comunicações com o reclamante."
    )

    # Conclusão e Resolução
    resolution_notes = models.TextField(
        blank=True,
        default='',
        verbose_name="Justificativa da Resolução",
        help_text="Fundamentação da decisão final adotada pela administração."
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data/Hora de Conclusão",
        help_text="Momento em que o caso foi formalmente encerrado."
    )

    # Auditoria de Usuários Responsáveis
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_takedowns',
        verbose_name="Registrado por"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_takedowns',
        verbose_name="Resolvido por"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Ocorrência de Contestação / Takedown"
        verbose_name_plural = "Ocorrências de Contestação / Takedown"
        ordering = ['-received_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'received_at']),
            models.Index(fields=['image_rights_record', 'status']),
        ]

    def __str__(self):
        status_label = dict(self.STATUS_CHOICES).get(self.status, self.status)
        claimant = self.claimant_name or self.claimant_email or "Anônimo"
        return f"Contestação #{self.pk} [{status_label}] - {claimant} ({self.image_rights_record})"

    @property
    def is_active(self):
        """Indica se a ocorrência está em andamento (não finalizada)."""
        return self.status in ['received', 'under_review', 'awaiting_information', 'temporarily_suspended']

    @property
    def is_blocking_display(self):
        """Indica se a ocorrência impõe suspensão da exibição pública da imagem."""
        return self.status in ['temporarily_suspended', 'resolved_removed']

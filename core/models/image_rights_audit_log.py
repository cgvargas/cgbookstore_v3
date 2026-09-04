# core/models/image_rights_audit_log.py
"""
Modelo Append-Only para Trilha Histórica de Auditoria e Governança de Direitos Autorais.
Registra eventos imutáveis de alterações em ImageRightsRecord, contestações e decisões administrativas.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class ImageRightsAuditLog(models.Model):
    """
    Trilha de auditoria append-only para governança de ativos visuais e direitos autorais.
    Registros são imutáveis após criados e bloqueados contra edição/exclusão pelo Admin ou aplicação.
    """

    EVENT_TYPE_CHOICES = [
        ('record_created', '✨ Registro Criado'),
        ('record_updated', '✏️ Registro Atualizado'),
        ('creator_changed', '👤 Autor/Criador Alterado'),
        ('rights_holder_changed', '🏛️ Titular dos Direitos Alterado'),
        ('licensor_changed', '🏢 Licenciante Alterado'),
        ('source_changed', '🌐 Fonte Original Alterada'),
        ('license_changed', '📄 Regime de Licença Alterado'),
        ('legal_basis_changed', '⚖️ Fundamento Jurídico Alterado'),
        ('audit_status_changed', '📊 Status de Auditoria Alterado'),
        ('public_display_changed', '👁️ Exibição Pública Alterada'),
        ('permission_document_changed', '📜 Documento Comprobatório Alterado'),
        ('takedown_received', '📥 Contestação Recebida'),
        ('takedown_status_changed', '🔄 Status da Contestação Alterado'),
        ('image_suspended', '⛔ Imagem Suspensa Preventivamente'),
        ('image_restored', '🟢 Exibição da Imagem Restaurada'),
        ('takedown_resolved_keep', '✅ Contestação Resolvida — Uso Mantido'),
        ('takedown_resolved_removed', '🛑 Contestação Resolvida — Imagem Retirada'),
        ('integrity_divergence_detected', '⚠️ Divergência de Integridade Detectada'),
        ('checksum_updated', '🔄 Checksum Recalculado/Atualizado'),
        ('provenance_registered', '🔗 Proveniência Técnica Registrada'),
        ('provenance_updated', '🔄 Proveniência Técnica Atualizada'),
        ('provenance_conflict_detected', '⚠️ Conflito de Proveniência Detectado'),
    ]

    SOURCE_CHOICES = [
        ('admin', 'Django Admin'),
        ('service', 'Serviço Interno'),
        ('command', 'Comando de Gerenciamento'),
        ('integration', 'Integração Externa / API'),
        ('migration', 'Migração / Importação'),
        ('system', 'Sistema / Automático'),
    ]

    image_rights_record = models.ForeignKey(
        'core.ImageRightsRecord',
        on_delete=models.PROTECT,
        related_name='audit_logs',
        db_index=True,
        verbose_name="Registro de Direitos Autorais",
        help_text="Ativo visual associado a este evento de governança."
    )

    event_type = models.CharField(
        max_length=40,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de Evento",
        help_text="Classificação estruturada do evento histórico."
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        db_index=True,
        verbose_name="Data/Hora do Evento",
        help_text="Momento exato em que o evento ocorreu (imutável)."
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='image_rights_audit_logs',
        verbose_name="Usuário Responsável",
        help_text="Administrador ou usuário que realizou ou autorizou a alteração."
    )

    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='service',
        db_index=True,
        verbose_name="Origem da Alteração",
        help_text="Canal ou processo de onde partiu a modificação."
    )

    field_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="Campo Alterado",
        help_text="Nome técnico do campo modificado, quando aplicável."
    )

    old_value = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Valor Anterior (Seguro)",
        help_text="Representação sanitizada do valor anterior (sem dados sensíveis ou caminhos privados)."
    )

    new_value = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Novo Valor (Seguro)",
        help_text="Representação sanitizada do novo valor."
    )

    description = models.CharField(
        max_length=500,
        verbose_name="Descrição do Evento",
        help_text="Resumo humano objetivo da ação executada."
    )

    takedown_request = models.ForeignKey(
        'core.CopyrightTakedownRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Contestação Relacionada",
        help_text="Notificação ou contestação associada a este evento, se houver."
    )

    metadata = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="Metadados Técnicos",
        help_text="Informações técnicas contextuais adicionais que não contenham dados pessoais ou arquivos confidenciais."
    )

    class Meta:
        verbose_name = "📜 Log de Auditoria de Direitos Autorais"
        verbose_name_plural = "📜 Trilha Histórica de Auditoria de Imagens"
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['image_rights_record', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['source', '-created_at']),
        ]

    def __str__(self):
        user_str = self.performed_by.username if self.performed_by else 'Sistema'
        return f"[{self.created_at.strftime('%d/%m/%Y %H:%M')}] {self.get_event_type_display()} por {user_str}"

    def clean(self):
        super().clean()
        if self.pk:
            # Proteção append-only no nível do model
            orig = ImageRightsAuditLog.objects.filter(pk=self.pk).first()
            if orig:
                raise ValidationError("Os registros da trilha de auditoria são imutáveis (append-only) e não podem ser editados.")

    def save(self, *args, **kwargs):
        # Se já existe PK no banco, bloquear alteração
        if self.pk:
            orig = ImageRightsAuditLog.objects.filter(pk=self.pk).first()
            if orig:
                raise ValidationError("Os registros da trilha de auditoria são imutáveis (append-only) e não podem ser editados.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Bloquear exclusão direta pelo Django ORM em circunstâncias normais
        raise ValidationError("Os registros da trilha de auditoria não podem ser excluídos da aplicação.")

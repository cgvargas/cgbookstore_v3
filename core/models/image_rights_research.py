# core/models/image_rights_research.py
"""
Modelo operacional para persistência de resultados de Pesquisa Assistida
de Direitos Autorais de Imagens (Fase 3A).

DIRETRIZ CENTRAL:
- Esta estrutura é OPERACIONAL, NÃO jurídica.
- Armazena propostas de preenchimento para revisão humana.
- NUNCA altera automaticamente audit_status, public_display_allowed ou legal_basis.
- A automação pesquisa, coleta, compara e propõe. O administrador confirma.
"""

from django.db import models
from django.conf import settings


class ImageRightsResearchResult(models.Model):
    """
    Resultado operacional de pesquisa assistida vinculado a um ImageRightsRecord.

    Armazena sugestões de preenchimento, fontes consultadas, conflitos e erros
    de forma estruturada para apresentação na tela de Auditoria Assistida.

    NÃO constitui decisão jurídica, autorização, licença ou parecer legal.
    """

    RESEARCH_STATUS_CHOICES = [
        ('not_started', '⏳ Não iniciada'),
        ('running', '🔄 Em andamento'),
        ('completed', '✅ Concluída'),
        ('partial', '⚠️ Parcial (fontes indisponíveis)'),
        ('failed', '❌ Falha técnica'),
    ]

    CONFIDENCE_CHOICES = [
        ('high', '🟢 Alta'),
        ('medium', '🟡 Média'),
        ('low', '🔴 Baixa'),
    ]

    image_rights_record = models.ForeignKey(
        'core.ImageRightsRecord',
        on_delete=models.CASCADE,
        related_name='research_results',
        verbose_name="Registro de Direitos Associado"
    )

    status = models.CharField(
        max_length=20,
        choices=RESEARCH_STATUS_CHOICES,
        default='not_started',
        db_index=True,
        verbose_name="Status da Pesquisa"
    )

    researched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data/Hora da Pesquisa"
    )
    researched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pesquisa realizada por"
    )

    # Dados internos utilizados como base para a pesquisa
    internal_data_used = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dados Internos Utilizados",
        help_text="Snapshot dos dados internos disponíveis no momento da pesquisa (ISBN, título, autor, editora, provider_asset_id, etc.)."
    )

    # Fontes consultadas durante a pesquisa
    sources_consulted = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Fontes Consultadas",
        help_text=(
            "Lista de fontes consultadas com status individual. "
            "Cada entrada: {source_name, source_type, url, status, retrieved_at, error}."
        )
    )

    # Sugestões de preenchimento para revisão humana
    suggestions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Sugestões de Preenchimento",
        help_text=(
            "Lista de propostas estruturadas. Cada entrada: "
            "{field_name, suggested_value, current_value, source_url, source_type, "
            "source_title, retrieved_at, confidence, short_reason, is_divergent}."
        )
    )

    # Conflitos entre fontes
    conflicts = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Conflitos Identificados",
        help_text=(
            "Divergências entre fontes confiáveis. "
            "Cada entrada: {field_name, source_a, value_a, source_b, value_b, note}."
        )
    )

    # Erros técnicos durante a pesquisa
    errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Erros Técnicos",
        help_text="Lista de erros de APIs ou fontes indisponíveis durante a pesquisa."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Resultado de Pesquisa Assistida"
        verbose_name_plural = "Resultados de Pesquisa Assistida"
        ordering = ['-researched_at']
        indexes = [
            models.Index(fields=['image_rights_record', '-researched_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Pesquisa #{self.pk} — Registro #{self.image_rights_record_id} ({self.get_status_display()})"

    @property
    def suggestion_count(self):
        """Total de sugestões encontradas."""
        return len(self.suggestions) if isinstance(self.suggestions, list) else 0

    @property
    def not_found_count(self):
        """Total de campos pesquisados sem resultado."""
        if not isinstance(self.suggestions, list):
            return 0
        return sum(1 for s in self.suggestions if not s.get('suggested_value'))

    @property
    def found_count(self):
        """Total de informações efetivamente encontradas."""
        if not isinstance(self.suggestions, list):
            return 0
        return sum(1 for s in self.suggestions if s.get('suggested_value'))

    @property
    def divergent_count(self):
        """Total de divergências com dados existentes."""
        if not isinstance(self.suggestions, list):
            return 0
        return sum(1 for s in self.suggestions if s.get('is_divergent'))

    @property
    def conflict_count(self):
        """Total de conflitos entre fontes."""
        return len(self.conflicts) if isinstance(self.conflicts, list) else 0

    @property
    def is_reusable(self):
        """
        Verifica se o resultado pode ser reutilizado (< 24h e status completed/partial).
        """
        if self.status not in ('completed', 'partial'):
            return False
        if not self.researched_at:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.researched_at) < timedelta(hours=24)

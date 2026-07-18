"""
Models do módulo Product Analytics — CG.BookStore v3.

Três entidades principais:
- AnalyticsSession: sessão web de um visitante (anônimo ou autenticado)
- ProductEvent:     evento comportamental rastreado durante a sessão
- DailyMetricSnapshot: snapshot diário de métricas agregadas

Design:
- Nenhum PII direto além do FK opcional para User
- IP bruto e User-Agent nunca armazenados
- Dados de busca representados por hash (nunca o termo literal)
- Compatível com LGPD: dados brutos com retenção de 90 dias,
  snapshots permanentes (sem PII)
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from typing import Optional

from .constants import (
    DEVICE_TYPE_CHOICES,
    DEVICE_TYPE_UNKNOWN,
    ALLOWED_EVENT_TYPES,
    ALLOWED_OBJECT_TYPES,
)


class AnalyticsSession(models.Model):
    """
    Representa uma sessão web de um visitante na plataforma.

    Uma sessão agrupa a atividade de um mesmo visitante (identificado
    pelo session_key do Django) durante uma janela de inatividade
    configurável (padrão: 30 minutos).

    Cobre tanto usuários anônimos (user=None) quanto autenticados.
    Nunca armazena IP completo ou User-Agent bruto.
    """

    # --------------------------------------------------------------------------
    # Identificação
    # --------------------------------------------------------------------------
    session_key = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name="Chave de Sessão",
        help_text="session_key do Django — identifica anônimos e autenticados",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_sessions",
        verbose_name="Usuário",
        help_text="Nulo para visitantes não autenticados",
    )
    is_authenticated = models.BooleanField(
        default=False,
        verbose_name="Autenticado",
        db_index=True,
    )

    # --------------------------------------------------------------------------
    # Timestamps da sessão
    # --------------------------------------------------------------------------
    started_at = models.DateTimeField(
        verbose_name="Início da Sessão",
        db_index=True,
    )
    last_activity_at = models.DateTimeField(
        verbose_name="Última Atividade",
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Encerramento da Sessão",
        help_text="Preenchido quando session_ended é registrado ou por timeout",
    )

    # --------------------------------------------------------------------------
    # Navegação
    # --------------------------------------------------------------------------
    entry_page = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Página de Entrada",
        help_text="Primeira página acessada nesta sessão (normalizada)",
    )
    exit_page = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Página de Saída",
        help_text="Última página acessada nesta sessão (normalizada)",
    )

    # --------------------------------------------------------------------------
    # Origem de tráfego
    # --------------------------------------------------------------------------
    referer_domain = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Domínio de Origem",
        help_text="Domínio do cabeçalho Referer sem path (ex: google.com)",
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Fonte (UTM Source)",
    )
    medium = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Meio (UTM Medium)",
    )
    campaign = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Campanha (UTM Campaign)",
    )

    # --------------------------------------------------------------------------
    # Dispositivo (derivados do UA — nunca o UA bruto)
    # --------------------------------------------------------------------------
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        default=DEVICE_TYPE_UNKNOWN,
        verbose_name="Tipo de Dispositivo",
        db_index=True,
    )
    browser_family = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Família do Navegador",
        help_text="Ex: Chrome, Firefox, Safari — sem versão",
    )
    operating_system = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Sistema Operacional",
        help_text="Ex: Windows, Android, iOS — sem versão",
    )

    # --------------------------------------------------------------------------
    # Metadados
    # --------------------------------------------------------------------------
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        verbose_name = "Sessão Analítica"
        verbose_name_plural = "Sessões Analíticas"
        ordering = ["-started_at"]
        indexes = [
            # Consultas por data (DAU/WAU/MAU)
            models.Index(fields=["-started_at"], name="pa_session_started_idx"),
            # Consultas por usuário
            models.Index(fields=["user", "-started_at"], name="pa_session_user_idx"),
            # Consultas por session_key (middleware)
            models.Index(fields=["session_key", "-started_at"], name="pa_session_key_idx"),
            # Filtros por dispositivo
            models.Index(fields=["device_type", "-started_at"], name="pa_session_device_idx"),
            # Filtros por autenticação
            models.Index(fields=["is_authenticated", "-started_at"], name="pa_session_auth_idx"),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else f"Anônimo({self.session_key[:8]})"
        started = self.started_at.strftime("%d/%m/%Y %H:%M") if self.started_at else "?"
        return f"Sessão {user_label} — {started}"

    @property
    def duration_seconds(self) -> Optional[int]:
        """
        Retorna a duração estimada da sessão em segundos.
        Usa ended_at se disponível, caso contrário last_activity_at.
        """
        if not self.started_at:
            return None
        end = self.ended_at or self.last_activity_at
        if not end:
            return None
        delta = end - self.started_at
        return max(0, int(delta.total_seconds()))

    @property
    def duration_minutes(self) -> Optional[float]:
        """Duração estimada em minutos."""
        secs = self.duration_seconds
        return round(secs / 60, 1) if secs is not None else None

    @property
    def is_active(self) -> bool:
        """
        Verifica se a sessão ainda está ativa (dentro do timeout configurado).
        """
        from .utils import get_analytics_settings
        cfg = get_analytics_settings()
        timeout_minutes = cfg.get("SESSION_TIMEOUT_MINUTES", 30)
        if not self.last_activity_at:
            return False
        elapsed = (timezone.now() - self.last_activity_at).total_seconds() / 60
        return elapsed < timeout_minutes and self.ended_at is None



class ProductEvent(models.Model):
    """
    Evento comportamental rastreado durante a navegação.

    Registra somente eventos que não possuem fonte canônica em outro app.
    Eventos duplicados (cliques de parceiros, adição de livros, etc.)
    são lidos diretamente das tabelas de origem.

    LGPD:
    - Nenhum PII direto além do FK opcional para User
    - Termos de busca representados por hash (SHA-256[:16])
    - metadata filtrado por allowlist de chaves
    """

    # --------------------------------------------------------------------------
    # Vinculação
    # --------------------------------------------------------------------------
    session = models.ForeignKey(
        AnalyticsSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="Sessão",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_events",
        verbose_name="Usuário",
    )

    # --------------------------------------------------------------------------
    # Evento
    # --------------------------------------------------------------------------
    event_type = models.CharField(
        max_length=50,
        verbose_name="Tipo de Evento",
        db_index=True,
        help_text="Somente valores da allowlist ALLOWED_EVENT_TYPES",
    )

    # --------------------------------------------------------------------------
    # Contexto de navegação
    # --------------------------------------------------------------------------
    page_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Nome da Página",
        help_text="Nome normalizado da página (não a URL bruta)",
        db_index=True,
    )
    object_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Tipo do Objeto",
        help_text="Ex: book, author, article (opcional)",
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID do Objeto",
        help_text="PK do objeto referenciado (opcional)",
    )

    # --------------------------------------------------------------------------
    # Dados adicionais
    # --------------------------------------------------------------------------
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados",
        help_text="Chaves restritas pela allowlist ALLOWED_METADATA_KEYS",
    )

    # --------------------------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------------------------
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registrado em",
        db_index=True,
    )

    class Meta:
        verbose_name = "Evento de Produto"
        verbose_name_plural = "Eventos de Produto"
        ordering = ["-created_at"]
        indexes = [
            # Consultas por tipo de evento no tempo (mais frequente)
            models.Index(fields=["event_type", "-created_at"], name="pa_event_type_idx"),
            # Consultas por usuário
            models.Index(fields=["user", "-created_at"], name="pa_event_user_idx"),
            # Consultas por sessão
            models.Index(fields=["session", "-created_at"], name="pa_event_session_idx"),
            # Consultas por página
            models.Index(fields=["page_name", "-created_at"], name="pa_event_page_idx"),
            # Purge por data (política de retenção)
            models.Index(fields=["created_at"], name="pa_event_created_purge_idx"),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else "Anônimo"
        return f"[{self.event_type}] {self.page_name or 'sem página'} — {user_label}"

    def clean(self):
        """Valida que event_type é da allowlist."""
        from django.core.exceptions import ValidationError
        if self.event_type and self.event_type not in ALLOWED_EVENT_TYPES:
            raise ValidationError(
                f"event_type '{self.event_type}' não permitido. "
                f"Valores válidos: {sorted(ALLOWED_EVENT_TYPES)}"
            )
        if self.object_type and self.object_type not in ALLOWED_OBJECT_TYPES:
            raise ValidationError(
                f"object_type '{self.object_type}' não permitido."
            )


class DailyMetricSnapshot(models.Model):
    """
    Snapshot diário de métricas de produto agregadas.

    Cada linha representa uma métrica, para uma data e (opcionalmente)
    uma dimensão de segmentação.

    Características:
    - Processamento idempotente (update_or_create por chave natural)
    - Pode ser reconstruído a partir de dados existentes para datas anteriores
    - is_partial=True indica que a métrica não pode ser completamente
      reconstruída historicamente (ex: page_views antes da implantação)
    - Sem PII: apenas dados agregados

    Exemplos de linhas:
        date=2026-07-17, metric_name=dau, value=342
        date=2026-07-17, metric_name=dau, dimension=device_type, dimension_value=mobile, value=198
        date=2026-07-17, metric_name=premium_conversions, value=7
    """

    # --------------------------------------------------------------------------
    # Chave
    # --------------------------------------------------------------------------
    date = models.DateField(
        verbose_name="Data",
        db_index=True,
    )
    metric_name = models.CharField(
        max_length=100,
        verbose_name="Nome da Métrica",
        db_index=True,
        help_text="Ex: dau, wau, mau, retention_d1, premium_conversions",
    )

    # --------------------------------------------------------------------------
    # Segmentação (opcional)
    # --------------------------------------------------------------------------
    dimension = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Dimensão",
        help_text="Ex: device_type, source, is_authenticated",
    )
    dimension_value = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Valor da Dimensão",
        help_text="Ex: mobile, google.com, true",
    )

    # --------------------------------------------------------------------------
    # Valor
    # --------------------------------------------------------------------------
    value = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name="Valor",
    )

    # --------------------------------------------------------------------------
    # Qualidade e auditoria
    # --------------------------------------------------------------------------
    source_apps = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Apps de Origem",
        help_text="Lista dos apps Django que contribuíram para o cálculo",
    )
    is_partial = models.BooleanField(
        default=False,
        verbose_name="Dados Parciais",
        help_text=(
            "True quando a métrica não pode ser completamente reconstruída "
            "para esta data (ex: rastreamento ainda não estava ativo)"
        ),
    )
    computed_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Computado em",
    )

    class Meta:
        verbose_name = "Snapshot de Métrica Diária"
        verbose_name_plural = "Snapshots de Métricas Diárias"
        ordering = ["-date", "metric_name"]
        # Chave natural: uma linha por (data, métrica, dimensão)
        unique_together = [
            ("date", "metric_name", "dimension", "dimension_value"),
        ]
        indexes = [
            # Range de datas para gráficos de séries temporais
            models.Index(fields=["-date", "metric_name"], name="pa_snapshot_date_metric_idx"),
            # Busca por métrica específica
            models.Index(fields=["metric_name", "-date"], name="pa_snapshot_metric_date_idx"),
        ]

    def __str__(self):
        dim_label = f" [{self.dimension}={self.dimension_value}]" if self.dimension else ""
        partial_label = " ⚠️partial" if self.is_partial else ""
        return f"{self.date} | {self.metric_name}{dim_label} = {self.value}{partial_label}"

    @classmethod
    def upsert(
        cls,
        date,
        metric_name: str,
        value,
        dimension: str = "",
        dimension_value: str = "",
        source_apps: list = None,
        is_partial: bool = False,
    ) -> "DailyMetricSnapshot":
        """
        Cria ou atualiza um snapshot de forma idempotente.

        Método principal para gravação — garante que recalcular a mesma
        métrica não gera duplicatas.
        """
        obj, _ = cls.objects.update_or_create(
            date=date,
            metric_name=metric_name,
            dimension=dimension,
            dimension_value=dimension_value,
            defaults={
                "value": value,
                "source_apps": source_apps or [],
                "is_partial": is_partial,
            },
        )
        return obj

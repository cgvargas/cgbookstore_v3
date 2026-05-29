"""
Models para o Sistema de Monitoramento do CG.BookStore.

Registra atividades suspeitas de usuários e problemas nas respostas
da IA, gerando alertas automáticos via WhatsApp para o administrador.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class SuspiciousActivity(models.Model):
    """
    Registra ocorrências de conduta inadequada ou suspeita de usuários.

    Cada instância representa um evento detectado automaticamente pelo
    SuspiciousActivityDetector durante uma interação no chat.
    """

    ACTIVITY_TYPES = [
        ('abusive_language', 'Linguagem Abusiva/Ofensiva'),
        ('spam', 'Spam (mensagens repetitivas)'),
        ('jailbreak_attempt', 'Tentativa de Jailbreak da IA'),
        ('illegal_content', 'Solicitação de Conteúdo Ilegal'),
        ('harassment', 'Assédio ou Ameaças'),
        ('personal_data_solicitation', 'Solicitação de Dados Pessoais'),
        ('other', 'Outro'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    # Quem enviou a mensagem suspeita
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspicious_activities',
        verbose_name='Usuário',
        help_text='Nulo para usuários anônimos'
    )

    # Sessão onde ocorreu a atividade
    session = models.ForeignKey(
        'chatbot_literario.ChatSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspicious_activities',
        verbose_name='Sessão de Chat'
    )

    # Mensagem específica que gerou o alerta
    message = models.ForeignKey(
        'chatbot_literario.ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspicious_activities',
        verbose_name='Mensagem'
    )

    # Tipo de atividade suspeita
    activity_type = models.CharField(
        max_length=40,
        choices=ACTIVITY_TYPES,
        default='other',
        verbose_name='Tipo de Atividade'
    )

    # Severidade detectada
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium',
        verbose_name='Severidade'
    )

    # Palavras/padrões que ativaram o detector
    detected_keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Palavras/Padrões Detectados',
        help_text='Lista de palavras ou padrões que ativaram o detector'
    )

    # Conteúdo da mensagem problemática (preview)
    message_content = models.TextField(
        verbose_name='Conteúdo da Mensagem',
        help_text='Conteúdo da mensagem que gerou o alerta'
    )

    # Chave de sessão para usuários anônimos
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Chave de Sessão Anônima'
    )

    # IP do usuário (para rastrear anônimos)
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP do Usuário'
    )

    # Controle de alertas e revisão
    alert_sent = models.BooleanField(
        default=False,
        verbose_name='Alerta WhatsApp Enviado',
        help_text='Se o alerta via WhatsApp já foi enviado ao administrador'
    )

    alert_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Alerta Enviado em'
    )

    reviewed = models.BooleanField(
        default=False,
        verbose_name='Revisado pelo Admin',
        help_text='Se o administrador já revisou esta ocorrência'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_activities',
        verbose_name='Revisado Por'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revisado em'
    )

    reviewer_notes = models.TextField(
        blank=True,
        verbose_name='Notas do Revisor',
        help_text='Observações do administrador após revisão'
    )

    # Ação tomada
    action_taken = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('none', 'Nenhuma ação'),
            ('warned', 'Usuário advertido'),
            ('suspended', 'Usuário suspenso'),
            ('banned', 'Usuário banido'),
            ('false_positive', 'Falso positivo'),
        ],
        verbose_name='Ação Tomada'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Detectado em'
    )

    class Meta:
        verbose_name = 'Atividade Suspeita'
        verbose_name_plural = 'Atividades Suspeitas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['reviewed', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['alert_sent']),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else f'Anônimo ({self.session_key or self.user_ip})'
        return f"[{self.get_severity_display()}] {self.get_activity_type_display()} — {user_label} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def mark_as_reviewed(self, reviewer, notes='', action='none'):
        """Marca a atividade como revisada pelo administrador."""
        self.reviewed = True
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.reviewer_notes = notes
        self.action_taken = action
        self.save(update_fields=['reviewed', 'reviewed_by', 'reviewed_at', 'reviewer_notes', 'action_taken'])

    def mark_alert_sent(self):
        """Marca que o alerta WhatsApp foi enviado."""
        self.alert_sent = True
        self.alert_sent_at = timezone.now()
        self.save(update_fields=['alert_sent', 'alert_sent_at'])

    @property
    def severity_emoji(self):
        """Retorna emoji correspondente à severidade."""
        return {
            'low': '🟡',
            'medium': '🟠',
            'high': '🔴',
            'critical': '🚨',
        }.get(self.severity, '⚪')

    @property
    def admin_url(self):
        """URL do painel admin para esta ocorrência."""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{site_url}/admin/monitoring/suspiciousactivity/{self.pk}/change/"


class AIResponseAlert(models.Model):
    """
    Registra problemas detectados nas respostas das IAs.

    Pode ser criado por:
    - Erros de API (timeout, quota excedida, etc.)
    - Reclamações explícitas dos usuários ("Reportar resposta")
    - Feedback negativo (👎 "Não útil" / "Incorreto")
    - Detecção automática de respostas vazias ou truncadas
    """

    ALERT_TYPES = [
        ('user_complaint', 'Reclamação Direta do Usuário'),
        ('negative_feedback', 'Feedback Negativo (👎)'),
        ('api_error', 'Erro de API da IA'),
        ('timeout', 'Timeout na resposta da IA'),
        ('empty_response', 'Resposta Vazia'),
        ('hallucination_suspected', 'Possível Alucinação da IA'),
        ('quota_exceeded', 'Quota da API Excedida'),
        ('content_filter', 'Filtro de Conteúdo Ativado'),
        ('other', 'Outro'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    AI_PROVIDERS = [
        ('gemini', 'Google Gemini'),
        ('groq', 'Groq'),
        ('unknown', 'Desconhecido'),
    ]

    # Sessão onde ocorreu o problema
    session = models.ForeignKey(
        'chatbot_literario.ChatSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_alerts',
        verbose_name='Sessão de Chat'
    )

    # Mensagem problemática da IA
    message = models.ForeignKey(
        'chatbot_literario.ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_alerts',
        verbose_name='Mensagem da IA'
    )

    # Usuário afetado
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_alerts',
        verbose_name='Usuário Afetado'
    )

    # Tipo de alerta
    alert_type = models.CharField(
        max_length=30,
        choices=ALERT_TYPES,
        default='other',
        verbose_name='Tipo de Alerta'
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium',
        verbose_name='Severidade'
    )

    # Qual provedor de IA estava sendo usado
    provider = models.CharField(
        max_length=20,
        choices=AI_PROVIDERS,
        default='unknown',
        verbose_name='Provedor de IA'
    )

    # Texto da reclamação (quando usuário reporta diretamente)
    user_complaint_text = models.TextField(
        blank=True,
        verbose_name='Texto da Reclamação',
        help_text='Texto descrito pelo usuário ao reportar o problema'
    )

    # Preview da resposta problemática
    ai_response_preview = models.TextField(
        blank=True,
        verbose_name='Prévia da Resposta da IA',
        help_text='Primeiros 500 caracteres da resposta problemática'
    )

    # Mensagem de erro técnico (quando é erro de API)
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensagem de Erro Técnico',
        help_text='Mensagem de erro retornada pela API da IA'
    )

    # Controle de alertas
    alert_sent = models.BooleanField(
        default=False,
        verbose_name='Alerta WhatsApp Enviado'
    )

    alert_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Alerta Enviado em'
    )

    # Resolução
    resolved = models.BooleanField(
        default=False,
        verbose_name='Resolvido'
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_ai_alerts',
        verbose_name='Resolvido Por'
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resolvido em'
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name='Notas de Resolução',
        help_text='O que foi feito para resolver o problema'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Alerta de IA'
        verbose_name_plural = 'Alertas de IA'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['alert_type', '-created_at']),
            models.Index(fields=['resolved', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['alert_sent']),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else 'Anônimo'
        return f"[{self.get_severity_display()}] {self.get_alert_type_display()} — {self.provider} — {user_label} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def mark_as_resolved(self, resolver, notes=''):
        """Marca o alerta como resolvido."""
        self.resolved = True
        self.resolved_by = resolver
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save(update_fields=['resolved', 'resolved_by', 'resolved_at', 'resolution_notes'])

    def mark_alert_sent(self):
        """Marca que o alerta WhatsApp foi enviado."""
        self.alert_sent = True
        self.alert_sent_at = timezone.now()
        self.save(update_fields=['alert_sent', 'alert_sent_at'])

    @property
    def severity_emoji(self):
        """Retorna emoji correspondente à severidade."""
        return {
            'low': '🟡',
            'medium': '🟠',
            'high': '🔴',
            'critical': '🚨',
        }.get(self.severity, '⚪')

    @property
    def admin_url(self):
        """URL do painel admin para este alerta."""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{site_url}/admin/monitoring/airesponsealert/{self.pk}/change/"

"""
Modelo para registrar exclusões de conta para análise e estatísticas.
"""
from django.db import models
from django.utils import timezone


class AccountDeletion(models.Model):
    """
    Registro de exclusão de conta para análise de churn e estatísticas.

    Armazena informações sobre usuários que excluíram suas contas,
    incluindo motivos, estatísticas e status de email.
    """

    # Motivos de exclusão
    REASON_CHOICES = [
        ('nao_uso_mais', 'Não uso mais o serviço'),
        ('falta_funcionalidades', 'Falta de funcionalidades necessárias'),
        ('dificuldade_uso', 'Dificuldade de uso / Interface confusa'),
        ('problemas_tecnicos', 'Problemas técnicos recorrentes'),
        ('preco_premium', 'Preço do Premium muito alto'),
        ('privacidade', 'Preocupações com privacidade'),
        ('migrando_plataforma', 'Migrando para outra plataforma'),
        ('conta_duplicada', 'Conta duplicada'),
        ('outros', 'Outros motivos'),
        ('nao_informado', 'Não informado'),
    ]

    # Informações do usuário (armazenadas antes da exclusão)
    username = models.CharField(
        max_length=150,
        verbose_name="Nome de usuário",
        help_text="Username do usuário que foi excluído"
    )

    email = models.EmailField(
        verbose_name="Email",
        help_text="Email do usuário excluído"
    )

    user_id = models.IntegerField(
        verbose_name="ID do usuário",
        help_text="ID original do usuário no banco de dados"
    )

    # Data e hora
    deleted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de exclusão",
        help_text="Data e hora em que a conta foi excluída"
    )

    user_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Conta criada em",
        help_text="Data de criação da conta do usuário"
    )

    # Motivo da exclusão
    deletion_reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        default='nao_informado',
        verbose_name="Motivo da exclusão",
        help_text="Motivo selecionado pelo usuário"
    )

    other_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Motivo personalizado",
        help_text="Motivo customizado quando selecionado 'Outros'"
    )

    # Estatísticas do usuário
    was_premium = models.BooleanField(
        default=False,
        verbose_name="Era Premium",
        help_text="Se o usuário tinha assinatura Premium ativa"
    )

    books_count = models.IntegerField(
        default=0,
        verbose_name="Quantidade de livros",
        help_text="Número de livros na biblioteca do usuário"
    )

    days_as_member = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias como membro",
        help_text="Quantos dias o usuário foi membro da plataforma"
    )

    # Status do email
    email_sent = models.BooleanField(
        default=False,
        verbose_name="Email enviado",
        help_text="Se o email de confirmação foi enviado com sucesso"
    )

    email_error = models.TextField(
        blank=True,
        null=True,
        verbose_name="Erro no email",
        help_text="Mensagem de erro caso o email tenha falhado"
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Email enviado em",
        help_text="Data e hora em que o email foi enviado"
    )

    # Dados adicionais
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Endereço IP",
        help_text="IP de onde a exclusão foi solicitada"
    )

    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="Informações do navegador/dispositivo"
    )

    # Notas administrativas
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas administrativas",
        help_text="Notas ou observações da equipe administrativa"
    )

    class Meta:
        verbose_name = "Exclusão de Conta"
        verbose_name_plural = "Exclusões de Contas"
        ordering = ['-deleted_at']
        indexes = [
            models.Index(fields=['-deleted_at']),
            models.Index(fields=['deletion_reason']),
            models.Index(fields=['was_premium']),
            models.Index(fields=['email_sent']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email}) - {self.get_deletion_reason_display()}"

    @property
    def deletion_reason_display(self):
        """Retorna o motivo completo (incluindo texto personalizado)."""
        if self.deletion_reason == 'outros' and self.other_reason:
            return f"Outros: {self.other_reason}"
        return self.get_deletion_reason_display()

    @property
    def membership_duration_display(self):
        """Retorna duração da assinatura formatada."""
        if not self.days_as_member:
            return "N/A"

        if self.days_as_member < 7:
            return f"{self.days_as_member} dias"
        elif self.days_as_member < 30:
            weeks = self.days_as_member // 7
            return f"{weeks} semana{'s' if weeks > 1 else ''}"
        elif self.days_as_member < 365:
            months = self.days_as_member // 30
            return f"{months} mês{'es' if months > 1 else ''}"
        else:
            years = self.days_as_member // 365
            return f"{years} ano{'s' if years > 1 else ''}"

    @property
    def email_status_display(self):
        """Retorna status do email formatado."""
        if self.email_sent:
            return "✅ Enviado com sucesso"
        elif self.email_error:
            return f"❌ Erro: {self.email_error[:50]}..."
        else:
            return "⏳ Não enviado"

    def save(self, *args, **kwargs):
        """Calcula dias como membro antes de salvar."""
        if self.user_created_at and not self.days_as_member:
            delta = self.deleted_at - self.user_created_at
            self.days_as_member = delta.days

        super().save(*args, **kwargs)

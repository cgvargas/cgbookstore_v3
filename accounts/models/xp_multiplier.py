"""
Model de Multiplicadores de XP do sistema de gamificação.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Aplicação do multiplicador
APPLIES_TO_CHOICES = [
    ('all', 'Todos os Usuários'),
    ('premium', 'Apenas Premium'),
    ('free', 'Apenas Free'),
]


class XPMultiplier(models.Model):
    """
    Multiplicadores de XP para eventos especiais e promoções.

    Permite aumentar temporariamente o XP ganho pelos usuários.
    """

    # ========== INFORMAÇÕES BÁSICAS ==========
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Multiplicador",
        help_text="Nome descritivo do evento/promoção"
    )

    description = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do multiplicador"
    )

    # ========== MULTIPLICADOR ==========
    multiplier_value = models.FloatField(
        default=1.5,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        verbose_name="Valor do Multiplicador",
        help_text="Multiplicador de XP (1.5 = +50%, 2.0 = +100%, etc)"
    )

    # ========== PERÍODO ==========
    start_date = models.DateTimeField(
        verbose_name="Data de Início",
        help_text="Quando o multiplicador começa a valer"
    )

    end_date = models.DateTimeField(
        verbose_name="Data de Término",
        help_text="Quando o multiplicador termina"
    )

    # ========== APLICAÇÃO ==========
    applies_to = models.CharField(
        max_length=20,
        choices=APPLIES_TO_CHOICES,
        default='all',
        verbose_name="Aplica-se a",
        help_text="Quem pode usar este multiplicador"
    )

    # ========== STATUS ==========
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Multiplicador está ativo"
    )

    # ========== METADADOS ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado Em"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado Em"
    )

    class Meta:
        verbose_name = "Multiplicador de XP"
        verbose_name_plural = "Multiplicadores de XP"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['applies_to']),
        ]

    def __str__(self):
        percentage = int((self.multiplier_value - 1) * 100)
        return f"{self.name} (+{percentage}% XP)"

    def is_active_now(self):
        """
        Verifica se o multiplicador está ativo no momento.

        Returns:
            bool: True se ativo, False caso contrário
        """
        if not self.is_active:
            return False

        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def applies_to_user(self, user):
        """
        Verifica se o multiplicador se aplica a um usuário específico.

        Args:
            user: Objeto User do Django

        Returns:
            bool: True se aplicável, False caso contrário
        """
        if not self.is_active_now():
            return False

        if self.applies_to == 'all':
            return True

        try:
            profile = user.profile

            if self.applies_to == 'premium':
                return profile.is_premium_active()
            elif self.applies_to == 'free':
                return not profile.is_premium_active()
        except:
            return False

        return False

    def get_display_info(self):
        """
        Retorna informações formatadas para exibição.

        Returns:
            dict: Dicionário com informações formatadas
        """
        percentage = int((self.multiplier_value - 1) * 100)

        return {
            'name': self.name,
            'description': self.description,
            'percentage': percentage,
            'percentage_display': f"+{percentage}%",
            'multiplier': self.multiplier_value,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active_now': self.is_active_now(),
            'applies_to_display': self.get_applies_to_display(),
        }

    @classmethod
    def get_current_multiplier_for_user(cls, user):
        """
        Retorna o multiplicador ativo aplicável ao usuário.
        Se houver múltiplos, retorna o maior.

        Args:
            user: Objeto User do Django

        Returns:
            float: Valor do multiplicador (1.0 = sem multiplicador)
        """
        now = timezone.now()

        # Buscar multiplicadores ativos que se aplicam ao usuário
        multipliers = cls.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )

        max_multiplier = 1.0

        for multiplier in multipliers:
            if multiplier.applies_to_user(user):
                max_multiplier = max(max_multiplier, multiplier.multiplier_value)

        return max_multiplier

    @classmethod
    def get_active_multipliers(cls):
        """
        Retorna todos os multiplicadores atualmente ativos.

        Returns:
            QuerySet: Multiplicadores ativos ordenados por valor
        """
        now = timezone.now()

        return cls.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-multiplier_value')

    @classmethod
    def create_event_multiplier(cls, name, multiplier_value, duration_days, applies_to='all'):
        """
        Cria um multiplicador de evento com duração específica.

        Args:
            name: Nome do evento
            multiplier_value: Valor do multiplicador
            duration_days: Duração em dias
            applies_to: A quem se aplica ('all', 'premium', 'free')

        Returns:
            XPMultiplier: Instância criada
        """
        from datetime import timedelta

        now = timezone.now()
        end_date = now + timedelta(days=duration_days)

        return cls.objects.create(
            name=name,
            multiplier_value=multiplier_value,
            start_date=now,
            end_date=end_date,
            applies_to=applies_to,
            is_active=True
        )

    def get_time_remaining(self):
        """
        Retorna o tempo restante do multiplicador.

        Returns:
            timedelta ou None: Tempo restante ou None se já expirou
        """
        if not self.is_active_now():
            return None

        now = timezone.now()
        return self.end_date - now

    def get_time_remaining_display(self):
        """
        Retorna o tempo restante formatado.

        Returns:
            str: Tempo restante em formato legível
        """
        remaining = self.get_time_remaining()

        if remaining is None:
            return "Expirado"

        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        if days > 0:
            return f"{days} dia(s) e {hours} hora(s)"
        elif hours > 0:
            return f"{hours} hora(s) e {minutes} minuto(s)"
        else:
            return f"{minutes} minuto(s)"
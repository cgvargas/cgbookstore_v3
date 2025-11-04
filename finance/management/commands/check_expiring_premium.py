"""
Comando Django para verificar e notificar sobre Premium expirando.

Este comando deve ser executado diariamente via cron job.
Envia notificações automáticas para usuários com Premium expirando em:
- 3 dias
- 1 dia
- No dia da expiração

Uso:
    python manage.py check_expiring_premium
    python manage.py check_expiring_premium --dry-run  # Simula sem enviar
    python manage.py check_expiring_premium --days 3   # Apenas 3 dias
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from finance.models import CampaignGrant
from accounts.models import CampaignNotification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica e notifica usuários sobre Premium expirando'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem enviar notificações',
        )
        parser.add_argument(
            '--days',
            type=int,
            choices=[1, 3],
            help='Verifica apenas para N dias (1 ou 3)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        specific_days = options.get('days')

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('VERIFICAÇÃO DE PREMIUM EXPIRANDO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma notificação será enviada'))

        self.stdout.write()

        now = timezone.now()
        total_notified = 0

        # Definir períodos de verificação
        periods = []
        if specific_days:
            periods = [(specific_days, f'{specific_days} dia(s)')]
        else:
            periods = [
                (3, '3 dias'),
                (1, '1 dia'),
                (0, 'hoje (último dia)'),
            ]

        for days_before, label in periods:
            self.stdout.write(f'\n>> Verificando Premium expirando em {label}...')

            # Calcular janela de tempo
            if days_before == 0:
                # Hoje: entre 00:00 e 23:59 de hoje
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                # N dias: entre 00:00 e 23:59 do dia N
                target_date = now.date() + timedelta(days=days_before)
                start = timezone.make_aware(
                    timezone.datetime.combine(target_date, timezone.datetime.min.time())
                )
                end = timezone.make_aware(
                    timezone.datetime.combine(target_date, timezone.datetime.max.time())
                )

            # Buscar concessões expirando neste período
            expiring_grants = CampaignGrant.objects.filter(
                is_active=True,
                expires_at__gte=start,
                expires_at__lte=end
            ).select_related('user', 'campaign', 'subscription')

            count = expiring_grants.count()
            self.stdout.write(f'   Encontradas: {count} concessao(oes)')

            if count == 0:
                continue

            # Processar cada concessão
            notified_count = 0
            for grant in expiring_grants:
                # Verificar se já foi notificado para este período
                already_notified = self._already_notified(grant, days_before)

                if already_notified:
                    self.stdout.write(
                        f'   [SKIP] {grant.user.username}: Ja notificado'
                    )
                    continue

                # Criar e enviar notificação
                if not dry_run:
                    try:
                        notification = CampaignNotification.create_expiring_notification(
                            user=grant.user,
                            grant=grant
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'   [OK] {grant.user.username}: Notificacao enviada (ID: {notification.id})'
                            )
                        )
                        notified_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'   [ERROR] {grant.user.username}: Erro ao enviar - {str(e)}'
                            )
                        )
                        logger.error(f'Erro ao enviar notificação para {grant.user.username}: {e}')
                else:
                    self.stdout.write(
                        f'   [NOTIFY] {grant.user.username}: Seria notificado (DRY-RUN)'
                    )
                    notified_count += 1

            total_notified += notified_count
            self.stdout.write(f'   Total notificado neste período: {notified_count}')

        # Resumo final
        self.stdout.write()
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('RESUMO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Total de notificacoes enviadas: {total_notified}')

        if dry_run:
            self.stdout.write(self.style.WARNING('(Modo DRY-RUN - nenhuma notificacao real foi enviada)'))

        self.stdout.write(self.style.SUCCESS('[SUCCESS] Comando executado com sucesso!'))

    def _already_notified(self, grant, days_before):
        """
        Verifica se já foi enviada notificação para este grant e período.

        Evita spam ao usuário verificando se já existe notificação de
        expiração criada hoje para esta concessão.
        """
        today = timezone.now().date()

        return CampaignNotification.objects.filter(
            user=grant.user,
            campaign_grant=grant,
            notification_type='premium_expiring',
            created_at__date=today
        ).exists()

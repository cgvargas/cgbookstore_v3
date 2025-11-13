"""
Comando Django para verificar e gerenciar assinaturas pagas.

Funções:
1. Verifica assinaturas expirando (7, 3, 1 dias) e envia emails de aviso
2. Desativa assinaturas expiradas
3. Sincroniza status com UserProfile
4. Gera relatório detalhado

Este comando deve ser executado diariamente via cron job.

Uso:
    python manage.py check_subscriptions
    python manage.py check_subscriptions --dry-run  # Simula sem fazer alterações
    python manage.py check_subscriptions --notify-days 7  # Notifica apenas 7 dias
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from finance.models import Subscription
from finance.notifications import (
    send_subscription_expiring_email,
    send_subscription_expired_email
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica e gerencia assinaturas pagas (expiração, notificações, desativação)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula execução sem fazer alterações ou enviar emails',
        )
        parser.add_argument(
            '--notify-days',
            type=int,
            choices=[1, 3, 7],
            help='Notifica apenas para N dias (1, 3 ou 7)',
        )
        parser.add_argument(
            '--skip-expired',
            action='store_true',
            help='Pula desativação de assinaturas expiradas',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        specific_days = options.get('notify_days')
        skip_expired = options.get('skip_expired', False)
        verbose = options.get('verbose', False)

        self.dry_run = dry_run
        self.verbose = verbose

        self._print_header('VERIFICAÇÃO DE ASSINATURAS PAGAS')

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: Nenhuma alteração será feita'))
            self.stdout.write()

        now = timezone.now()
        stats = {
            'notified_7_days': 0,
            'notified_3_days': 0,
            'notified_1_day': 0,
            'expired_deactivated': 0,
            'errors': 0
        }

        # 1. Notificar assinaturas expirando
        self._print_section('1. NOTIFICAÇÕES DE EXPIRAÇÃO')

        notification_periods = []
        if specific_days:
            notification_periods = [(specific_days, f'{specific_days} dia(s)')]
        else:
            notification_periods = [
                (7, '7 dias'),
                (3, '3 dias'),
                (1, '1 dia'),
            ]

        for days_before, label in notification_periods:
            count = self._notify_expiring(now, days_before, label, stats)
            if days_before == 7:
                stats['notified_7_days'] = count
            elif days_before == 3:
                stats['notified_3_days'] = count
            elif days_before == 1:
                stats['notified_1_day'] = count

        # 2. Desativar assinaturas expiradas
        if not skip_expired:
            self.stdout.write()
            self._print_section('2. DESATIVAÇÃO DE ASSINATURAS EXPIRADAS')
            stats['expired_deactivated'] = self._deactivate_expired(now)

        # 3. Sincronizar com UserProfile
        self.stdout.write()
        self._print_section('3. SINCRONIZAÇÃO COM USERPROFILE')
        self._sync_userprofiles()

        # 4. Relatório final
        self.stdout.write()
        self._print_report(stats)

    def _notify_expiring(self, now, days_before, label, stats):
        """Notifica usuários com assinatura expirando em N dias"""
        self.stdout.write(f'\n📧 Verificando assinaturas expirando em {label}...')

        # Calcular janela de tempo para o dia específico
        target_date = (now + timedelta(days=days_before)).date()
        start = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        )
        end = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.max.time())
        )

        # Buscar assinaturas ativas expirando neste período
        expiring_subs = Subscription.objects.filter(
            status='ativa',
            expiration_date__gte=start,
            expiration_date__lte=end
        ).select_related('user')

        count = expiring_subs.count()
        self.stdout.write(f'   Encontradas: {count} assinatura(s)')

        if count == 0:
            return 0

        notified = 0
        for subscription in expiring_subs:
            user = subscription.user
            username = user.username

            # Verifica se já foi notificado hoje (evita spam)
            if self._was_notified_today(subscription, days_before):
                if self.verbose:
                    self.stdout.write(f'   [SKIP] {username}: Já notificado hoje')
                continue

            # Envia email de aviso
            if not self.dry_run:
                try:
                    success = send_subscription_expiring_email(subscription, days_before)
                    if success:
                        # Marca como notificado (poderia adicionar campo no model)
                        self.stdout.write(
                            self.style.SUCCESS(f'   [✓] {username}: Email enviado ({user.email})')
                        )
                        notified += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'   [!] {username}: Falha ao enviar email')
                        )
                        stats['errors'] += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   [✗] {username}: Erro - {str(e)}')
                    )
                    logger.error(f'Erro ao notificar {username}: {e}', exc_info=True)
                    stats['errors'] += 1
            else:
                self.stdout.write(f'   [DRY-RUN] {username}: Seria notificado')
                notified += 1

        self.stdout.write(f'   Total notificado: {notified}')
        return notified

    def _deactivate_expired(self, now):
        """Desativa assinaturas que já expiraram"""
        self.stdout.write('\n🔒 Verificando assinaturas expiradas...')

        # Buscar assinaturas ativas mas já expiradas
        expired_subs = Subscription.objects.filter(
            status='ativa',
            expiration_date__lt=now
        ).select_related('user')

        count = expired_subs.count()
        self.stdout.write(f'   Encontradas: {count} assinatura(s) expirada(s)')

        if count == 0:
            return 0

        deactivated = 0
        for subscription in expired_subs:
            user = subscription.user
            username = user.username

            if not self.dry_run:
                try:
                    # Cancela a assinatura
                    subscription.cancel()
                    subscription.status = 'expirada'  # Status mais específico
                    subscription.save()

                    # Envia email informando
                    send_subscription_expired_email(subscription)

                    # Atualiza UserProfile
                    try:
                        profile = user.userprofile
                        profile.is_premium = False
                        profile.premium_expires_at = None
                        profile.save()
                    except:
                        pass

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   [✓] {username}: Desativada (expirou em {subscription.expiration_date.strftime("%d/%m/%Y")})'
                        )
                    )
                    deactivated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   [✗] {username}: Erro ao desativar - {str(e)}')
                    )
                    logger.error(f'Erro ao desativar {username}: {e}', exc_info=True)
            else:
                self.stdout.write(
                    f'   [DRY-RUN] {username}: Seria desativada (expirou {subscription.expiration_date.strftime("%d/%m/%Y")})'
                )
                deactivated += 1

        self.stdout.write(f'   Total desativado: {deactivated}')
        return deactivated

    def _sync_userprofiles(self):
        """Sincroniza status de assinaturas com UserProfile"""
        self.stdout.write('\n🔄 Sincronizando status com UserProfile...')

        # Buscar todas as assinaturas ativas
        active_subs = Subscription.objects.filter(
            status='ativa',
            expiration_date__gt=timezone.now()
        ).select_related('user')

        synced = 0
        for subscription in active_subs:
            try:
                profile = subscription.user.userprofile

                # Verifica se está dessincronizado
                needs_sync = (
                    not profile.is_premium or
                    profile.premium_expires_at != subscription.expiration_date
                )

                if needs_sync:
                    if not self.dry_run:
                        profile.is_premium = True
                        profile.premium_expires_at = subscription.expiration_date
                        profile.save()

                    if self.verbose:
                        self.stdout.write(
                            f'   [✓] {subscription.user.username}: Sincronizado'
                        )
                    synced += 1

            except Exception as e:
                if self.verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'   [!] {subscription.user.username}: UserProfile não encontrado'
                        )
                    )

        self.stdout.write(f'   Total sincronizado: {synced}')

    def _was_notified_today(self, subscription, days_before):
        """
        Verifica se já foi enviado email hoje para esta assinatura.

        Nota: Isso é uma simplificação. Em produção, você poderia adicionar
        um campo 'last_notification_sent' no model ou usar cache.
        """
        # Por simplicidade, vamos assumir que não foi notificado
        # Em produção, adicione um campo no model para tracking
        return False

    def _print_header(self, title):
        """Imprime cabeçalho formatado"""
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(title))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write()

    def _print_section(self, title):
        """Imprime seção formatada"""
        self.stdout.write(self.style.SUCCESS(f'\n{title}'))
        self.stdout.write(self.style.SUCCESS('-' * len(title)))

    def _print_report(self, stats):
        """Imprime relatório final"""
        self._print_header('RELATÓRIO FINAL')

        self.stdout.write(f'📊 Notificações enviadas:')
        self.stdout.write(f'   • 7 dias antes: {stats["notified_7_days"]}')
        self.stdout.write(f'   • 3 dias antes: {stats["notified_3_days"]}')
        self.stdout.write(f'   • 1 dia antes:  {stats["notified_1_day"]}')
        total_notified = stats["notified_7_days"] + stats["notified_3_days"] + stats["notified_1_day"]
        self.stdout.write(f'   Total: {total_notified}')

        self.stdout.write(f'\n🔒 Assinaturas desativadas: {stats["expired_deactivated"]}')

        if stats['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f'\n⚠️  Erros encontrados: {stats["errors"]}')
            )

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  MODO DRY-RUN: Nenhuma alteração foi feita')
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Comando executado com sucesso!'))

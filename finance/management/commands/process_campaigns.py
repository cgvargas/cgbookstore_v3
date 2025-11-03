"""
Management command para processar campanhas de marketing automaticamente
Uso: python manage.py process_campaigns
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from finance.models import Campaign
from finance.services import CampaignService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Processa campanhas ativas e concede/revoga Premium automaticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='ID de uma campanha específica para processar'
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Apenas pré-visualiza sem conceder Premiums'
        )
        parser.add_argument(
            '--check-expired',
            action='store_true',
            help='Verifica e revoga concessões expiradas'
        )

    def handle(self, *args, **options):
        campaign_id = options.get('campaign_id')
        preview = options.get('preview', False)
        check_expired = options.get('check_expired', False)

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🎯 PROCESSADOR DE CAMPANHAS DE MARKETING'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # 1. Verifica concessões expiradas
        if check_expired or not campaign_id:
            self.stdout.write('🔍 Verificando concessões expiradas...')
            result = CampaignService.check_expired_grants()
            if result['success']:
                revoked = result['revoked_count']
                if revoked > 0:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️  {revoked} concessão(ões) expirada(s) revogada(s)')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('   ✅ Nenhuma concessão expirada encontrada')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro: {result.get("error")}')
                )
            self.stdout.write('')

        # 2. Processa campanhas
        now = timezone.now()

        if campaign_id:
            # Processa campanha específica
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                campaigns = [campaign]
                self.stdout.write(f'🎯 Processando campanha específica: {campaign.name}')
            except Campaign.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Campanha ID {campaign_id} não encontrada')
                )
                return
        else:
            # Busca todas as campanhas ativas no período
            campaigns = Campaign.objects.filter(
                status='active',
                auto_grant=True,
                start_date__lte=now,
                end_date__gte=now
            )
            self.stdout.write(f'🔍 Buscando campanhas ativas...')
            self.stdout.write(f'   📊 {campaigns.count()} campanha(s) ativa(s) encontrada(s)')
            self.stdout.write('')

        if not campaigns:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhuma campanha ativa para processar')
            )
            return

        # Processa cada campanha
        total_granted = 0
        total_eligible = 0
        campaigns_processed = 0

        for campaign in campaigns:
            self.stdout.write('-' * 70)
            self.stdout.write(f'📢 Campanha: {campaign.name}')
            self.stdout.write(f'   Tipo: {campaign.get_target_type_display()}')
            self.stdout.write(f'   Duração: {campaign.duration_days} dias')
            self.stdout.write(f'   Limite: {campaign.max_grants or "Ilimitado"}')

            # Verifica se ainda pode conceder
            if not campaign.can_grant_more():
                self.stdout.write(
                    self.style.WARNING('   ⚠️  Limite de concessões atingido')
                )
                continue

            # Executa campanha
            result = CampaignService.execute_campaign(campaign, preview=preview)

            if result['success']:
                eligible_count = result['eligible_count']
                granted_count = result.get('granted_count', 0)

                total_eligible += eligible_count
                total_granted += granted_count
                campaigns_processed += 1

                if preview:
                    self.stdout.write(
                        self.style.WARNING(
                            f'   👀 PREVIEW: {eligible_count} usuários elegíveis'
                        )
                    )
                    # Mostra primeiros 5 usuários
                    eligible_users = result.get('eligible_users', [])[:5]
                    for user in eligible_users:
                        self.stdout.write(f'      • {user["username"]} ({user["email"]})')
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'   ✅ {granted_count}/{eligible_count} Premiums concedidos'
                        )
                    )

                # Mostra erros se houver
                errors = result.get('errors', [])
                if errors:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️  {len(errors)} erro(s):')
                    )
                    for error in errors[:5]:  # Mostra apenas os primeiros 5
                        self.stdout.write(f'      • {error}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro: {result.get("error")}')
                )

        # Resumo final
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'Campanhas processadas: {campaigns_processed}')
        self.stdout.write(f'Usuários elegíveis: {total_eligible}')

        if preview:
            self.stdout.write(
                self.style.WARNING(f'MODO PREVIEW - Nenhum Premium foi concedido')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Total de Premiums concedidos: {total_granted}')
            )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🎉 Processamento concluído com sucesso!')
        )
        self.stdout.write('')

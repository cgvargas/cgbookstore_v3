"""
Comando de management para testar o sistema de monitoramento e WhatsApp.

Uso:
    python manage.py test_monitoring --check         # Verificar configuracao
    python manage.py test_monitoring --whatsapp      # Enviar mensagem de teste
    python manage.py test_monitoring --stats         # Ver estatisticas
    python manage.py test_monitoring --daily-summary # Disparar resumo diario
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = 'Testa o sistema de monitoramento e alertas WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument('--whatsapp', action='store_true', help='Envia mensagem de teste via WhatsApp')
        parser.add_argument('--check', action='store_true', help='Verifica a configuracao')
        parser.add_argument('--stats', action='store_true', help='Exibe estatisticas atuais')
        parser.add_argument('--daily-summary', action='store_true', help='Dispara o resumo diario')

    def handle(self, *args, **options):
        if options['check']:
            self._check_config()
        elif options['whatsapp']:
            self._test_whatsapp()
        elif options['stats']:
            self._show_stats()
        elif options['daily_summary']:
            self._send_daily_summary()
        else:
            self._check_config()
            self.stdout.write('\nUse --whatsapp para enviar mensagem de teste')

    def _check_config(self):
        """Verifica se a configuracao esta correta."""
        self.stdout.write(self.style.HTTP_INFO('\n[*] Verificando configuracao do sistema de monitoramento...\n'))

        phone = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '')
        api_key = getattr(settings, 'CALLMEBOT_API_KEY', '')

        if phone and api_key:
            self.stdout.write(self.style.SUCCESS('[OK] WhatsApp configurado'))
            self.stdout.write(f'   Numero: {phone[:4]}****{phone[-2:] if len(phone) > 6 else ""}')
            self.stdout.write(f'   API Key: {api_key[:4]}****')
        else:
            self.stdout.write(self.style.WARNING('[!!] WhatsApp NAO configurado'))
            if not phone:
                self.stdout.write(self.style.ERROR('   [X] WHATSAPP_ADMIN_NUMBER nao definido no .env'))
            if not api_key:
                self.stdout.write(self.style.ERROR('   [X] CALLMEBOT_API_KEY nao definido no .env'))
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('   SETUP CALLMEBOT (5 minutos):'))
            self.stdout.write('   1. Salve o numero +34644001121 nos contatos do WhatsApp')
            self.stdout.write('   2. Envie: "I allow callmebot to send me messages"')
            self.stdout.write('   3. Receba sua API KEY por WhatsApp')
            self.stdout.write('   4. Configure no .env:')
            self.stdout.write('      WHATSAPP_ADMIN_NUMBER=5511999998888')
            self.stdout.write('      CALLMEBOT_API_KEY=XXXXXXXX')

        self.stdout.write('')
        spam_threshold = getattr(settings, 'MONITORING_SPAM_THRESHOLD', 5)
        spam_window = getattr(settings, 'MONITORING_SPAM_WINDOW_SECONDS', 60)
        min_severity = getattr(settings, 'MONITORING_ALERT_MIN_SEVERITY', 'medium')

        self.stdout.write(self.style.SUCCESS('[OK] Configuracoes de deteccao:'))
        self.stdout.write(f'   Threshold de spam: {spam_threshold} msgs em {spam_window}s')
        self.stdout.write(f'   Severidade minima para alerta: {min_severity}')

    def _test_whatsapp(self):
        """Envia mensagem de teste via WhatsApp."""
        self.stdout.write(self.style.HTTP_INFO('\n[WA] Enviando mensagem de teste via WhatsApp...\n'))

        from monitoring.whatsapp_service import get_whatsapp_notifier
        notifier = get_whatsapp_notifier()

        if not notifier.enabled:
            self.stdout.write(self.style.ERROR('[X] WhatsApp nao configurado. Use --check para ver instrucoes.'))
            return

        success = notifier.send_test_message()

        if success:
            self.stdout.write(self.style.SUCCESS(
                f'[OK] Mensagem de teste enviada com sucesso para {notifier.phone}!'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                '[X] Falha ao enviar mensagem. Verifique os logs para mais detalhes.'
            ))

    def _show_stats(self):
        """Exibe estatisticas atuais do monitoramento."""
        from monitoring.models import SuspiciousActivity, AIResponseAlert
        from datetime import timedelta

        self.stdout.write(self.style.HTTP_INFO('\n[STATS] Estatisticas de Monitoramento\n'))

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        self.stdout.write(self.style.HTTP_INFO('[!] Condutas Suspeitas:'))
        total_24h = SuspiciousActivity.objects.filter(created_at__gte=last_24h).count()
        total_7d = SuspiciousActivity.objects.filter(created_at__gte=last_7d).count()
        critical = SuspiciousActivity.objects.filter(created_at__gte=last_24h, severity='critical').count()
        high = SuspiciousActivity.objects.filter(created_at__gte=last_24h, severity='high').count()
        unreviewed = SuspiciousActivity.objects.filter(reviewed=False).count()

        self.stdout.write(f'   Ultimas 24h: {total_24h} (criticas: {critical}, altas: {high})')
        self.stdout.write(f'   Ultimos 7 dias: {total_7d}')
        self.stdout.write(f'   Nao revisadas (total): {unreviewed}')

        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('[IA] Alertas de IA:'))
        ai_24h = AIResponseAlert.objects.filter(created_at__gte=last_24h).count()
        ai_7d = AIResponseAlert.objects.filter(created_at__gte=last_7d).count()
        ai_critical = AIResponseAlert.objects.filter(created_at__gte=last_24h, severity='critical').count()
        ai_unresolved = AIResponseAlert.objects.filter(resolved=False).count()
        user_complaints = AIResponseAlert.objects.filter(
            created_at__gte=last_24h, alert_type='user_complaint'
        ).count()

        self.stdout.write(f'   Ultimas 24h: {ai_24h} (criticos: {ai_critical})')
        self.stdout.write(f'   Ultimos 7 dias: {ai_7d}')
        self.stdout.write(f'   Reclamacoes de usuarios (24h): {user_complaints}')
        self.stdout.write(f'   Nao resolvidos (total): {ai_unresolved}')

        self.stdout.write('')
        pending_suspicious = SuspiciousActivity.objects.filter(
            alert_sent=False, severity__in=['high', 'critical']
        ).count()
        pending_ai = AIResponseAlert.objects.filter(
            alert_sent=False, severity__in=['high', 'critical']
        ).count()

        if pending_suspicious + pending_ai > 0:
            self.stdout.write(self.style.WARNING(
                f'[!!] {pending_suspicious + pending_ai} alertas WhatsApp pendentes de envio'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('[OK] Nenhum alerta pendente'))

    def _send_daily_summary(self):
        """Dispara o resumo diario via WhatsApp."""
        self.stdout.write(self.style.HTTP_INFO('\n[*] Disparando resumo diario...\n'))
        from monitoring.tasks import send_daily_monitoring_summary
        send_daily_monitoring_summary()
        self.stdout.write(self.style.SUCCESS('[OK] Resumo diario processado!'))

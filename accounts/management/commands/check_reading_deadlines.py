"""
Comando Django para verificar prazos de leitura e criar notificações.

Execução manual:
    python manage.py check_reading_deadlines

Execução com opções:
    python manage.py check_reading_deadlines --dry-run
    python manage.py check_reading_deadlines --verbose
    python manage.py check_reading_deadlines --clean-old

Agendar no Windows Task Scheduler:
    - Programa: python
    - Argumentos: manage.py check_reading_deadlines
    - Pasta inicial: C:\ProjectDjango\cgbookstore_v3
    - Horário: Diariamente às 9:00
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from accounts.models import ReadingProgress, ReadingNotification
from datetime import datetime


class Command(BaseCommand):
    help = 'Verifica prazos de leitura, cria notificações e abandona livros automaticamente'

    def add_arguments(self, parser):
        """Adiciona argumentos de linha de comando."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução',
        )
        parser.add_argument(
            '--clean-old',
            action='store_true',
            help='Remove notificações lidas com mais de 30 dias',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Dias para considerar notificações antigas (padrão: 30)',
        )

    def handle(self, *args, **options):
        """Executa o comando."""
        dry_run = options['dry_run']
        verbose = options['verbose']
        clean_old = options['clean_old']
        days = options['days']

        # Timestamp de início
        start_time = timezone.now()

        # Header
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("🔍 VERIFICAÇÃO DE PRAZOS DE LEITURA"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"⏰ Horário: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  MODO DRY-RUN: Nenhuma alteração será feita"))

        self.stdout.write("")

        # Contadores
        stats = {
            'deadline_warnings': 0,
            'deadline_passed': 0,
            'books_abandoned': 0,
            'notifications_created': 0,
            'notifications_cleaned': 0,
        }

        try:
            # ========== 1. VERIFICAR PRAZOS PRÓXIMOS ==========
            self.stdout.write("📅 Verificando prazos próximos...")

            stats['deadline_warnings'] = self._check_deadline_warnings(
                dry_run=dry_run,
                verbose=verbose
            )

            self.stdout.write(
                self.style.SUCCESS(f"   ✅ {stats['deadline_warnings']} notificação(ões) de prazo próximo")
            )

            # ========== 2. VERIFICAR PRAZOS VENCIDOS ==========
            self.stdout.write("\n⏰ Verificando prazos vencidos...")

            stats['deadline_passed'] = self._check_deadline_passed(
                dry_run=dry_run,
                verbose=verbose
            )

            self.stdout.write(
                self.style.WARNING(f"   ⚠️  {stats['deadline_passed']} notificação(ões) de prazo vencido")
            )

            # ========== 3. ABANDONAR LIVROS AUTOMATICAMENTE ==========
            self.stdout.write("\n🗑️  Verificando livros para abandono automático...")

            stats['books_abandoned'] = self._auto_abandon_books(
                dry_run=dry_run,
                verbose=verbose
            )

            if stats['books_abandoned'] > 0:
                self.stdout.write(
                    self.style.ERROR(f"   🚨 {stats['books_abandoned']} livro(s) abandonado(s)")
                )
            else:
                self.stdout.write("   ✅ Nenhum livro para abandonar")

            # ========== 4. LIMPAR NOTIFICAÇÕES ANTIGAS ==========
            if clean_old:
                self.stdout.write(f"\n🧹 Limpando notificações lidas com mais de {days} dias...")

                stats['notifications_cleaned'] = self._clean_old_notifications(
                    days=days,
                    dry_run=dry_run,
                    verbose=verbose
                )

                self.stdout.write(
                    f"   ✅ {stats['notifications_cleaned']} notificação(ões) removida(s)"
                )

            # ========== 5. ESTATÍSTICAS FINAIS ==========
            stats['notifications_created'] = (
                    stats['deadline_warnings'] +
                    stats['deadline_passed'] +
                    stats['books_abandoned']
            )

            # Tempo de execução
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()

            # Resumo
            self.stdout.write("\n" + "=" * 70)
            self.stdout.write(self.style.SUCCESS("📊 RESUMO DA EXECUÇÃO"))
            self.stdout.write("=" * 70)
            self.stdout.write(f"   📢 Notificações criadas: {stats['notifications_created']}")
            self.stdout.write(f"      - Prazo próximo: {stats['deadline_warnings']}")
            self.stdout.write(f"      - Prazo vencido: {stats['deadline_passed']}")
            self.stdout.write(f"      - Livro abandonado: {stats['books_abandoned']}")

            if clean_old:
                self.stdout.write(f"   🧹 Notificações limpas: {stats['notifications_cleaned']}")

            self.stdout.write(f"   ⏱️  Tempo de execução: {duration:.2f}s")
            self.stdout.write("=" * 70 + "\n")

            if dry_run:
                self.stdout.write(self.style.WARNING("⚠️  MODO DRY-RUN: Nenhuma alteração foi feita\n"))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ ERRO: {str(e)}\n")
            )
            raise

    def _check_deadline_warnings(self, dry_run=False, verbose=False):
        """
        Verifica livros com prazo próximo (5 dias ou menos).

        Returns:
            int: Quantidade de notificações criadas
        """
        count = 0

        # Buscar progressos com prazo próximo
        progressos = ReadingProgress.objects.filter(
            deadline__isnull=False,
            finished_at__isnull=True,
            is_abandoned=False,
            deadline_notified=False
        ).select_related('user', 'book')

        for progress in progressos:
            # Verificar se deve notificar
            if progress.should_notify_deadline:
                if verbose:
                    self.stdout.write(
                        f"   📌 {progress.user.username} - {progress.book.title} "
                        f"(faltam {progress.days_until_deadline} dias)"
                    )

                if not dry_run:
                    # Criar notificação
                    notification = ReadingNotification.create_deadline_warning(progress)

                    if notification:
                        # Marcar como notificado
                        progress.mark_deadline_notified()
                        count += 1

        return count

    def _check_deadline_passed(self, dry_run=False, verbose=False):
        """
        Verifica livros com prazo vencido.

        Returns:
            int: Quantidade de notificações criadas
        """
        count = 0

        # Buscar progressos com prazo vencido
        progressos = ReadingProgress.objects.filter(
            deadline__isnull=False,
            deadline__lt=timezone.now().date(),
            finished_at__isnull=True,
            is_abandoned=False
        ).select_related('user', 'book')

        for progress in progressos:
            if progress.is_overdue:
                # Verificar se já não foi notificado hoje
                today = timezone.now().date()
                already_notified = ReadingNotification.objects.filter(
                    user=progress.user,
                    reading_progress=progress,
                    notification_type='deadline_passed',
                    created_at__date=today
                ).exists()

                if not already_notified:
                    if verbose:
                        self.stdout.write(
                            f"   ⏰ {progress.user.username} - {progress.book.title} "
                            f"(atrasado {progress.days_overdue} dias)"
                        )

                    if not dry_run:
                        notification = ReadingNotification.create_deadline_passed(progress)
                        if notification:
                            count += 1

        return count

    def _auto_abandon_books(self, dry_run=False, verbose=False):
        """
        Abandona automaticamente livros com 5+ dias de atraso.

        Returns:
            int: Quantidade de livros abandonados
        """
        count = 0

        # Buscar progressos que devem ser abandonados
        progressos = ReadingProgress.objects.filter(
            deadline__isnull=False,
            finished_at__isnull=True,
            is_abandoned=False
        ).select_related('user', 'book')

        for progress in progressos:
            if progress.should_auto_abandon:
                if verbose:
                    self.stdout.write(
                        f"   🗑️  {progress.user.username} - {progress.book.title} "
                        f"(atrasado {progress.days_overdue} dias)"
                    )

                if not dry_run:
                    # Abandonar o livro
                    success = progress.mark_as_abandoned(auto=True)

                    if success:
                        # Criar notificação
                        ReadingNotification.create_book_abandoned(progress)
                        count += 1

        return count

    def _clean_old_notifications(self, days=30, dry_run=False, verbose=False):
        """
        Remove notificações lidas antigas.

        Args:
            days (int): Dias para considerar antigas

        Returns:
            int: Quantidade de notificações removidas
        """
        if dry_run:
            # No dry-run, apenas contar
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=days)

            count = ReadingNotification.objects.filter(
                is_read=True,
                read_at__lt=cutoff_date
            ).count()

            if verbose and count > 0:
                self.stdout.write(
                    f"   🧹 Seriam removidas {count} notificação(ões)"
                )

            return count
        else:
            # Remover de verdade
            return ReadingNotification.delete_old_notifications(days=days)
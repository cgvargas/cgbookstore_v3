"""
Command: compute_daily_metrics

Calcula ou reconstrói snapshots analíticos diários.
Suporta cálculo de um dia específico ou intervalo de datas (backfill).

Uso:
  python manage.py compute_daily_metrics                  # Ontem (padrão)
  python manage.py compute_daily_metrics --date 2026-07-16
  python manage.py compute_daily_metrics --start 2026-07-01 --end 2026-07-15
"""
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from product_analytics.services.snapshot_service import SnapshotService


class Command(BaseCommand):
    help = "Consolida snapshots de métricas diárias para o Product Analytics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Data específica em formato AAAA-MM-DD para calcular",
        )
        parser.add_argument(
            "--start",
            type=str,
            help="Data de início (AAAA-MM-DD) para um intervalo de backfill",
        )
        parser.add_argument(
            "--end",
            type=str,
            help="Data de fim (AAAA-MM-DD) para um intervalo de backfill",
        )

    def handle(self, *args, **options):
        # 1. Parsing da data específica
        if options["date"]:
            try:
                target_date = datetime.datetime.strptime(options["date"], "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("Data inválida. Use o formato AAAA-MM-DD.")

            self.stdout.write(f"Iniciando cálculo para a data específica: {target_date}")
            snapshots = SnapshotService.compute_day(target_date)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cálculo concluído! {len(snapshots)} métricas consolidadas para {target_date}."
                )
            )
            return

        # 2. Parsing de intervalo (backfill)
        if options["start"] or options["end"]:
            if not (options["start"] and options["end"]):
                raise CommandError("Ambas as opções --start e --end devem ser informadas juntas.")

            try:
                start_date = datetime.datetime.strptime(options["start"], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(options["end"], "%Y-%m-%d").date()
            except ValueError:
                raise CommandError("Data inválida no intervalo. Use o formato AAAA-MM-DD.")

            if start_date > end_date:
                raise CommandError("A data de início (--start) deve ser anterior ou igual à data de fim (--end).")

            self.stdout.write(f"Iniciando backfill de {start_date} até {end_date}...")
            total = SnapshotService.backfill_range(start_date, end_date)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backfill concluído! Total de {total} snapshots salvos."
                )
            )
            return

        # 3. Padrão: Ontem
        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        self.stdout.write(f"Nenhum argumento fornecido. Computando dados de ontem ({yesterday})...")
        snapshots = SnapshotService.compute_day(yesterday)
        self.stdout.write(
            self.style.SUCCESS(
                f"Consolidação de ontem concluída! {len(snapshots)} snapshots gravados."
            )
        )

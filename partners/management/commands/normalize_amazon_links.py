"""
Management Command para normalizar e padronizar todos os links da Amazon Brasil cadastrados no sistema.

Uso:
  python manage.py normalize_amazon_links --dry-run
  python manage.py normalize_amazon_links --apply
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from core.models import Book
from partners.services.amazon_service import AmazonURLNormalizer


class Command(BaseCommand):
    help = (
        "Analisa e normaliza todos os links da Amazon Brasil para o padrão "
        "https://www.amazon.com.br/dp/{ASIN}?tag={AMAZON_ASSOCIATE_TAG}"
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Modo de simulação: analisa os links e exibe as alterações sem modificar o banco de dados.',
        )
        group.add_argument(
            '--apply',
            action='store_true',
            default=False,
            help='Executa a atualização real dos registros no banco de dados dentro de uma transação.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        apply_mode = options['apply']

        # Se nenhum argumento for passado expressamente, adota --dry-run como segurança
        if not apply_mode and not dry_run:
            dry_run = True

        mode_label = "EXECUCAO REAL (--apply)" if apply_mode else "SIMULACAO (--dry-run)"
        self.stdout.write(self.style.MIGRATE_HEADING(f"=== NORMALIZACAO DE LINKS DA AMAZON BRASIL: {mode_label} ==="))

        if apply_mode:
            self.stdout.write(
                self.style.WARNING(
                    "ATENCAO: Recomenda-se realizar o backup do banco de dados antes da execucao real."
                )
            )


        tag = AmazonURLNormalizer.get_associate_tag()
        self.stdout.write(f"Tag de associado alvo: {tag}")
        self.stdout.write("-" * 80)

        # Filtrar livros relacionados à Amazon
        all_books = Book.objects.all().order_by('id')
        amazon_books = [
            b for b in all_books
            if (b.purchase_partner_name and b.purchase_partner_name.strip().lower() == 'amazon')
            or (b.purchase_partner_url and AmazonURLNormalizer.is_amazon_url(b.purchase_partner_url))
        ]

        total_analyzed = len(amazon_books)
        total_already_correct = 0
        total_to_update = 0
        total_failed = 0

        changes = []
        already_correct_list = []
        needs_manual_review = []

        for book in amazon_books:
            old_url = (book.purchase_partner_url or '').strip()

            if not old_url:
                needs_manual_review.append((book.id, book.title, old_url, "Livro cadastrado como Amazon, mas sem URL de compra."))
                total_failed += 1
                continue

            # Verificar se é link encurtado (ex: amzn.to)
            if 'amzn.to' in old_url.lower():
                needs_manual_review.append((book.id, book.title, old_url, "Link encurtado (amzn.to). Requer resolução manual do destino final."))
                total_failed += 1
                continue

            try:
                new_url = AmazonURLNormalizer.normalize(old_url, associate_tag=tag)
            except ValueError as exc:
                needs_manual_review.append((book.id, book.title, old_url, f"Erro ao identificar ASIN: {exc}"))
                total_failed += 1
                continue

            if old_url == new_url:
                total_already_correct += 1
                already_correct_list.append((book.id, book.title, old_url))
            else:
                total_to_update += 1
                changes.append((book, old_url, new_url))

        # Exibir relatório detalhado das alterações
        if changes:
            self.stdout.write(self.style.SUCCESS(f"\n[REGISTROS PARA ALTERACAO ({len(changes)})]"))
            for book, old_url, new_url in changes:
                self.stdout.write(f"  * ID {book.id} | Livro: {book.title[:50]}")
                self.stdout.write(f"    - URL Anterior: {old_url}")
                self.stdout.write(f"    + Nova URL:     {new_url}\n")

        if already_correct_list:
            self.stdout.write(f"\n[REGISTROS JA PADRONIZADOS ({len(already_correct_list)})]")
            for b_id, title, url in already_correct_list:
                self.stdout.write(f"  [OK] ID {b_id} | {title[:50]} -> {url}")

        if needs_manual_review:
            self.stdout.write(self.style.WARNING(f"\n[REGISTROS QUE REQUEREM REVISAO MANUAL ({len(needs_manual_review)})]"))
            for b_id, title, url, reason in needs_manual_review:
                self.stdout.write(f"  [X] ID {b_id} | {title[:50]}")
                self.stdout.write(f"     URL: {url or '(Vazia)'}")
                self.stdout.write(f"     Motivo: {reason}\n")

        # Se for modo real (--apply), efetuar alterações em transação atômica
        if apply_mode and changes:
            self.stdout.write("\nAplicando alteracoes no banco de dados...")
            with transaction.atomic():
                for book, old_url, new_url in changes:
                    book.purchase_partner_url = new_url
                    # Garante que o nome do parceiro seja padronizado como "Amazon" se estava em branco
                    if not book.purchase_partner_name:
                        book.purchase_partner_name = "Amazon"
                    book.save(update_fields=['purchase_partner_url', 'purchase_partner_name', 'updated_at'])
            self.stdout.write(self.style.SUCCESS(f"[OK] Sucesso! {len(changes)} registros foram atualizados no banco de dados."))
        elif dry_run and changes:
            self.stdout.write(self.style.NOTICE(f"\nModo SIMULACAO (--dry-run). Nenhuma alteracao foi salva no banco. Use --apply para efetivar."))

        # Resumo executivo final
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("RESUMO DA EXECUCAO:"))
        self.stdout.write(f"  - Total de registros da Amazon analisados : {total_analyzed}")
        self.stdout.write(f"  - Registros que serao/foram alterados     : {total_to_update}")
        self.stdout.write(f"  - Registros que ja estavam padronizados   : {total_already_correct}")
        self.stdout.write(f"  - Registros com pendencias (revisao)      : {total_failed}")
        self.stdout.write("=" * 80 + "\n")


"""
Comando de Gerenciamento para Sincronizar Metadados de Livros com a Amazon Brasil e Fontes Externas.
"""

from django.core.management.base import BaseCommand
from core.models import Book
from partners.services.amazon_api_service import AmazonAPIService
from core.services.book_metadata_aggregator import BookMetadataAggregator


class Command(BaseCommand):
    help = 'Sincroniza metadados dos livros com a API da Amazon Brasil e Agregador Multidesconto'

    def add_arguments(self, parser):
        parser.add_argument('--isbn', type=str, help='ISBN específico para sincronizar')
        parser.add_argument('--book-id', type=int, help='ID do livro no banco de dados')
        parser.add_argument('--all', action='store_true', help='Sincronizar todos os livros cadastrados')
        parser.add_argument('--force', action='store_true', help='Substituir campos já preenchidos')

    def handle(self, *args, **options):
        status = AmazonAPIService.get_status()
        self.stdout.write(self.style.MIGRATE_HEADING("=== STATUS DA INTEGRAÇÃO AMAZON BRASIL ==="))
        self.stdout.write(f"Status: {status['mode_display']}")
        self.stdout.write(f"Tag de Associado: {status['associate_tag']}")
        self.stdout.write(f"API Habilitada: {status['enabled']} | Modo Mock: {status['mock_mode']}\n")

        isbn = options.get('isbn')
        book_id = options.get('book_id')
        sync_all = options.get('all')
        force = options.get('force', False)

        if isbn:
            data = AmazonAPIService.search_by_isbn(isbn)
            if data:
                self.stdout.write(self.style.SUCCESS(f"✅ Produto encontrado na Amazon:"))
                self.stdout.write(f"   ASIN: {data.asin}")
                self.stdout.write(f"   Título: {data.title}")
                self.stdout.write(f"   Autor: {data.author}")
                self.stdout.write(f"   Preço: R$ {data.price:.2f}" if data.price else "   Preço: N/A")
                self.stdout.write(f"   Link Afiliado: {data.affiliate_url}")
                self.stdout.write(f"   Fonte de Dados: {data.source}")
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ NENHUM produto encontrado na Amazon para o ISBN: {isbn}"))
            return

        queryset = Book.objects.all()
        if book_id:
            queryset = queryset.filter(id=book_id)
        elif not sync_all:
            self.stdout.write(self.style.ERROR("Informe --isbn, --book-id ou --all para executar a sincronização."))
            return

        total = queryset.count()
        self.stdout.write(f"Iniciando sincronização de {total} livro(s)...\n")

        updated_count = 0
        for book in queryset:
            res = BookMetadataAggregator.fetch_and_enrich_book(book, force=force)
            if res['changes']:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"[UPDATED] {book.title} ({len(res['changes'])} alterações)"))
                for change in res['changes']:
                    self.stdout.write(f"   - {change}")
            else:
                self.stdout.write(f"[OK] {book.title} (nenhuma alteração necessária)")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Sincronização concluída! {updated_count}/{total} livro(s) atualizados."))

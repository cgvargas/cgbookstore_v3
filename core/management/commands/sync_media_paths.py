"""
Management command para sincronizar paths de mídia entre Banco de Dados e Supabase
Corrige inconsistências entre nomes de arquivos no DB vs Storage
Uso: python manage.py sync_media_paths [--dry-run]
CG.BookStore v3
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Book
from core.utils.supabase_storage import supabase_storage_admin
import os
from typing import Dict, List


class Command(BaseCommand):
    help = 'Sincroniza paths de mídia entre Banco de Dados e Supabase Storage'

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a sincronização sem fazer alterações no banco',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra detalhes adicionais durante a execução',
        )

    def handle(self, *args, **options):
        """Executa o comando de sincronização"""
        dry_run = options['dry_run']
        verbose = options['verbose']

        self.stdout.write(self.style.WARNING('\n' + '=' * 70))
        self.stdout.write(self.style.WARNING('  SINCRONIZAÇÃO DE PATHS - BANCO vs SUPABASE'))
        self.stdout.write(self.style.WARNING('=' * 70 + '\n'))

        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 MODO DRY-RUN: Nenhuma alteração será feita\n'))

        # 1. Carregar arquivos do Supabase
        self.stdout.write('📥 Carregando arquivos do Supabase...')
        supabase_files = self._load_supabase_files()

        if not supabase_files:
            self.stdout.write(self.style.ERROR('❌ Erro ao carregar arquivos do Supabase'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ {len(supabase_files)} arquivos carregados\n'))

        # 2. Processar livros
        self.stdout.write('📚 Processando livros...')
        books = Book.objects.filter(
            cover_image__isnull=False
        ).exclude(cover_image='')

        total_books = books.count()
        self.stdout.write(f'   Total: {total_books} livros com imagem\n')

        # Estatísticas
        stats = {
            'encontrados': 0,
            'nao_encontrados': 0,
            'ja_corretos': 0,
            'corrigidos': 0,
            'erros': 0
        }

        # 3. Processar cada livro
        with transaction.atomic():
            for i, book in enumerate(books, 1):
                result = self._process_book(
                    book,
                    supabase_files,
                    dry_run,
                    verbose,
                    i,
                    total_books
                )
                stats[result] += 1

            if dry_run:
                # Reverter transação no dry-run
                transaction.set_rollback(True)

        # 4. Mostrar resumo
        self._print_summary(stats, dry_run)

    def _load_supabase_files(self) -> List[str]:
        """
        Carrega lista de todos os arquivos do bucket book-covers

        Returns:
            Lista com nomes dos arquivos
        """
        try:
            files = supabase_storage_admin.list_files('book-covers', '', limit=500)
            return [f.get('name', '') for f in files if f.get('name')]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao listar arquivos: {str(e)}'))
            return []

    def _process_book(
            self,
            book: Book,
            supabase_files: List[str],
            dry_run: bool,
            verbose: bool,
            index: int,
            total: int
    ) -> str:
        """
        Processa um livro individual

        Args:
            book: Instância do livro
            supabase_files: Lista de arquivos no Supabase
            dry_run: Se True, não salva alterações
            verbose: Se True, mostra detalhes
            index: Índice atual
            total: Total de livros

        Returns:
            String indicando o resultado: 'encontrados', 'nao_encontrados',
            'ja_corretos', 'corrigidos', 'erros'
        """
        progress = f'[{index}/{total}]'

        try:
            # Path atual no banco
            current_path = book.cover_image.name

            # Extrair nome do arquivo (sem books/covers/)
            current_filename = current_path.split('/')[-1]

            # Verificar se o arquivo existe exatamente como está
            if current_filename in supabase_files:
                if verbose:
                    self.stdout.write(
                        f'   {progress} ✅ {book.title[:40]} - '
                        f'{self.style.SUCCESS("Já correto")}'
                    )
                return 'ja_corretos'

            # Tentar encontrar arquivo similar
            matched_file = self._find_matching_file(current_filename, supabase_files)

            if matched_file:
                # Construir novo path
                new_path = f'books/covers/{matched_file}'

                self.stdout.write(
                    f'   {progress} 🔧 {book.title[:40]}'
                )
                self.stdout.write(
                    f'      DE: {current_filename}'
                )
                self.stdout.write(
                    f'      PARA: {matched_file}'
                )

                if not dry_run:
                    book.cover_image = new_path
                    book.save(update_fields=['cover_image'])

                return 'corrigidos'
            else:
                # Não encontrou correspondência
                self.stdout.write(
                    f'   {progress} ⚠️  {book.title[:40]} - '
                    f'{self.style.WARNING("Arquivo não encontrado")}'
                )
                if verbose:
                    self.stdout.write(f'      Procurando: {current_filename}')

                return 'nao_encontrados'

        except Exception as e:
            self.stdout.write(
                f'   {progress} ❌ {book.title[:40]} - '
                f'{self.style.ERROR(f"Erro: {str(e)}")}'
            )
            return 'erros'

    def _find_matching_file(self, filename: str, supabase_files: List[str]) -> str:
        """
        Procura arquivo correspondente no Supabase

        Estratégia:
        1. Busca exata
        2. Busca sem sufixo Django (_XXXXX)
        3. Busca por nome base (sem extensão)

        Args:
            filename: Nome do arquivo no DB
            supabase_files: Lista de arquivos no Supabase

        Returns:
            Nome do arquivo encontrado ou string vazia
        """
        # 1. Busca exata
        if filename in supabase_files:
            return filename

        # 2. Busca sem sufixo Django
        # Ex: o-problema-dos-tres-corpos_pRFjeVJ.jpg → o-problema-dos-tres-corpos
        base_name = filename.rsplit('_', 1)[0]  # Remove último _XXXXX
        ext = os.path.splitext(filename)[1]  # .jpg

        # Procurar arquivo que comece com base_name
        for file in supabase_files:
            if file.startswith(base_name):
                return file

        # 3. Busca por nome base (sem extensão)
        # Ex: kaiju-no-8-vol-1.jpg → kaiju-no-8-vol-1
        name_without_ext = os.path.splitext(filename)[0]

        for file in supabase_files:
            file_without_ext = os.path.splitext(file)[0]
            if file_without_ext == name_without_ext:
                return file

        return ''

    def _print_summary(self, stats: Dict[str, int], dry_run: bool):
        """Imprime resumo final da sincronização"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.WARNING('  RESUMO DA SINCRONIZAÇÃO'))
        self.stdout.write('=' * 70 + '\n')

        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 MODO DRY-RUN (simulação)\n'))

        total = sum(stats.values())
        self.stdout.write(f'📊 Total de livros processados: {total}\n')

        if stats['ja_corretos'] > 0:
            self.stdout.write(
                f'✅ Já corretos: '
                f'{self.style.SUCCESS(str(stats["ja_corretos"]))}'
            )

        if stats['corrigidos'] > 0:
            action = 'Seriam corrigidos' if dry_run else 'Corrigidos com sucesso'
            self.stdout.write(
                f'🔧 {action}: '
                f'{self.style.SUCCESS(str(stats["corrigidos"]))}'
            )

        if stats['nao_encontrados'] > 0:
            self.stdout.write(
                f'⚠️  Não encontrados no Supabase: '
                f'{self.style.WARNING(str(stats["nao_encontrados"]))}'
            )

        if stats['erros'] > 0:
            self.stdout.write(
                f'❌ Erros: '
                f'{self.style.ERROR(str(stats["erros"]))}'
            )

        self.stdout.write('')

        # Mensagem final
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Simulação concluída!\n'
                    '   Execute sem --dry-run para aplicar as correções.'
                )
            )
        elif stats['corrigidos'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Sincronização concluída! {stats["corrigidos"]} livro(s) corrigido(s).\n'
                    '   As imagens devem aparecer corretamente agora.'
                )
            )
        elif stats['ja_corretos'] == total:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Todos os livros já estão com paths corretos!\n'
                    '   Nenhuma alteração necessária.'
                )
            )

        if stats['nao_encontrados'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠️  Atenção: {stats["nao_encontrados"]} arquivo(s) não encontrado(s) no Supabase.\n'
                    '   Você pode precisar fazer upload manual desses arquivos.'
                )
            )

        self.stdout.write('')
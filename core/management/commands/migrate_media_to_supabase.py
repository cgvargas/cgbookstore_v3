"""
Management command para migrar arquivos de mídia local para Supabase Storage
Uso: python manage.py migrate_media_to_supabase [--dry-run]
CG.BookStore v3
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from core.utils.supabase_storage import supabase_storage_admin
import os
from pathlib import Path
from typing import List, Tuple
import mimetypes


class Command(BaseCommand):
    help = 'Migra arquivos de mídia locais para o Supabase Storage'

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a migração sem fazer upload real',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Pula arquivos que já existem no Supabase',
        )

    def handle(self, *args, **options):
        """Executa o comando de migração"""
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']

        self.stdout.write(self.style.WARNING('\n' + '=' * 70))
        self.stdout.write(self.style.WARNING('  MIGRAÇÃO DE MÍDIA LOCAL → SUPABASE STORAGE'))
        self.stdout.write(self.style.WARNING('=' * 70 + '\n'))

        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 MODO DRY-RUN: Nenhum arquivo será enviado\n'))

        # Verificar configurações
        if not self._check_config():
            return

        # Verificar e criar buckets
        if not dry_run:
            self._setup_buckets()

        # Definir mapeamentos de pastas para buckets
        migrations = [
            ('books/covers', supabase_storage_admin.BOOK_COVERS_BUCKET, 'Capas de Livros'),
            ('authors/photos', supabase_storage_admin.AUTHOR_PHOTOS_BUCKET, 'Fotos de Autores'),
            ('events', supabase_storage_admin.BOOK_COVERS_BUCKET, 'Imagens de Eventos'),
            ('users', supabase_storage_admin.USER_AVATARS_BUCKET, 'Avatares de Usuários'),
        ]

        # Estatísticas
        total_files = 0
        total_success = 0
        total_skipped = 0
        total_errors = 0

        # Processar cada tipo de mídia
        for folder, bucket, description in migrations:
            self.stdout.write(f'\n📁 Processando: {self.style.SUCCESS(description)}')
            self.stdout.write(f'   Pasta local: {folder}/')
            self.stdout.write(f'   Bucket: {bucket}\n')

            files = self._get_files_in_folder(folder)

            if not files:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Nenhum arquivo encontrado em {folder}/\n'))
                continue

            self.stdout.write(f'   📊 Encontrados: {len(files)} arquivo(s)')

            # Migrar arquivos
            success, skipped, errors = self._migrate_files(
                files, bucket, folder, dry_run, skip_existing
            )

            total_files += len(files)
            total_success += success
            total_skipped += skipped
            total_errors += errors

        # Resumo final
        self._print_summary(total_files, total_success, total_skipped, total_errors, dry_run)

    def _check_config(self) -> bool:
        """Verifica se as configurações do Supabase estão corretas"""
        self.stdout.write('🔍 Verificando configurações...')

        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            self.stdout.write(
                self.style.ERROR(
                    '\n❌ ERRO: Configurações do Supabase não encontradas!\n'
                    'Verifique as variáveis SUPABASE_URL e SUPABASE_ANON_KEY no .env'
                )
            )
            return False

        self.stdout.write(self.style.SUCCESS('✅ Configurações OK\n'))
        return True

    def _setup_buckets(self):
        """Cria os buckets necessários no Supabase"""
        self.stdout.write('🪣 Configurando buckets no Supabase...')
        try:
            supabase_storage_admin.create_buckets()
            self.stdout.write(self.style.SUCCESS('✅ Buckets configurados\n'))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Aviso ao configurar buckets: {str(e)}\n')
            )

    def _get_files_in_folder(self, folder: str) -> List[Path]:
        """
        Lista todos os arquivos em uma pasta da mídia local

        Args:
            folder: Path relativo dentro de MEDIA_ROOT

        Returns:
            Lista de objetos Path dos arquivos encontrados
        """
        media_root = Path(settings.MEDIA_ROOT)
        folder_path = media_root / folder

        if not folder_path.exists():
            return []

        # Listar todos os arquivos recursivamente
        files = []
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                # Ignorar arquivos do sistema
                if not file_path.name.startswith('.'):
                    files.append(file_path)

        return sorted(files)

    def _migrate_files(
            self,
            files: List[Path],
            bucket: str,
            base_folder: str,
            dry_run: bool,
            skip_existing: bool
    ) -> Tuple[int, int, int]:
        """
        Migra lista de arquivos para o Supabase

        Args:
            files: Lista de arquivos a migrar
            bucket: Nome do bucket destino
            base_folder: Pasta base (para calcular path relativo)
            dry_run: Se True, não faz upload real
            skip_existing: Se True, pula arquivos existentes

        Returns:
            Tupla (sucessos, pulados, erros)
        """
        media_root = Path(settings.MEDIA_ROOT)
        success = 0
        skipped = 0
        errors = 0

        for i, file_path in enumerate(files, 1):
            # Calcular path relativo
            relative_path = file_path.relative_to(media_root / base_folder)

            # Construir path no bucket (sem a pasta base)
            folder_in_bucket = str(relative_path.parent) if relative_path.parent != Path('.') else ''
            filename = file_path.name

            # Barra de progresso
            progress = f'[{i}/{len(files)}]'

            try:
                if dry_run:
                    self.stdout.write(
                        f'   {progress} 🔍 {self.style.NOTICE(filename)} '
                        f'→ {bucket}/{folder_in_bucket}'
                    )
                    success += 1
                    continue

                # Verificar se já existe (se solicitado)
                if skip_existing:
                    path_to_check = f"{folder_in_bucket}/{filename}" if folder_in_bucket else filename
                    files_in_bucket = supabase_storage_admin.list_files(bucket, folder_in_bucket)
                    if any(f.get('name') == filename for f in files_in_bucket):
                        self.stdout.write(
                            f'   {progress} ⏭️  {self.style.WARNING(filename)} '
                            f'(já existe)'
                        )
                        skipped += 1
                        continue

                # Fazer upload
                with open(file_path, 'rb') as file:
                    url = supabase_storage_admin.upload_file(
                        file=file,
                        bucket=bucket,
                        folder=folder_in_bucket,
                        filename=filename
                    )

                if url:
                    self.stdout.write(
                        f'   {progress} ✅ {self.style.SUCCESS(filename)}'
                    )
                    success += 1
                else:
                    self.stdout.write(
                        f'   {progress} ❌ {self.style.ERROR(filename)} '
                        f'(upload falhou)'
                    )
                    errors += 1

            except Exception as e:
                self.stdout.write(
                    f'   {progress} ❌ {self.style.ERROR(filename)} '
                    f'(erro: {str(e)})'
                )
                errors += 1

        return success, skipped, errors

    def _print_summary(
            self,
            total: int,
            success: int,
            skipped: int,
            errors: int,
            dry_run: bool
    ):
        """Imprime resumo final da migração"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.WARNING('  RESUMO DA MIGRAÇÃO'))
        self.stdout.write('=' * 70 + '\n')

        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 MODO DRY-RUN (simulação)\n'))

        self.stdout.write(f'📊 Total de arquivos processados: {total}')

        if success > 0:
            emoji = '🔍' if dry_run else '✅'
            action = 'Simulados' if dry_run else 'Migrados com sucesso'
            self.stdout.write(
                f'{emoji} {action}: '
                f'{self.style.SUCCESS(str(success))}'
            )

        if skipped > 0:
            self.stdout.write(
                f'⏭️  Pulados (já existem): '
                f'{self.style.WARNING(str(skipped))}'
            )

        if errors > 0:
            self.stdout.write(
                f'❌ Erros: '
                f'{self.style.ERROR(str(errors))}'
            )

        self.stdout.write('')

        if dry_run and errors == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Simulação concluída sem erros!\n'
                    '   Execute sem --dry-run para fazer a migração real.'
                )
            )
        elif not dry_run and errors == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '🎉 Migração concluída com sucesso!\n'
                    '   Todos os arquivos foram enviados para o Supabase Storage.'
                )
            )
        elif errors > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'⚠️  Migração concluída com {errors} erro(s).\n'
                    '   Verifique os logs acima para mais detalhes.'
                )
            )

        self.stdout.write('')
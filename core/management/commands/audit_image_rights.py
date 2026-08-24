# core/management/commands/audit_image_rights.py
"""
Comando de Gerenciamento Django para Auditoria e Rastreamento Automatizado de Imagens.
Sincroniza dimensões, calcula hashes SHA-256, cria registros de procedência padrão
para mídias sem registro e exibe o resumo de conformidade no terminal.
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import Book, Author, LiteraryUniverse, Banner, Section, Event
from news.models import Article, Quiz
from core.models.image_rights import ImageRightsRecord
from core.services.image_rights_service import ImageRightsAuditService


class Command(BaseCommand):
    help = "Executa a auditoria e rastreamento completo de ativos visuais em toda a aplicação."

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-create',
            action='store_true',
            help='Cria automaticamente um ImageRightsRecord básico para campos de imagem sem registro.',
        )

    def handle(self, *args, **options):
        auto_create = options.get('auto_create', False)
        models_to_audit = [Book, Author, LiteraryUniverse, Article, Quiz, Event, Banner, Section]

        self.stdout.write(self.style.SUCCESS("[INFO] Iniciando Auditoria e Rastreamento Corporativo de Imagens...\n"))

        total_analyzed = 0
        total_created = 0
        total_updated = 0
        total_missing = 0

        for model_cls in models_to_audit:
            model_name = model_cls._meta.verbose_name_plural.title()
            ct = ContentType.objects.get_for_model(model_cls)

            image_fields = [
                f for f in model_cls._meta.get_fields()
                if isinstance(f, (models.ImageField, models.FileField))
            ]

            if not image_fields:
                continue

            self.stdout.write(f"[*] Auditando {model_name} (Campos: {', '.join([f.name for f in image_fields])})...")

            for obj in model_cls.objects.all():
                for f in image_fields:
                    file_attr = getattr(obj, f.name, None)
                    if not file_attr or not hasattr(file_attr, 'name') or not file_attr.name:
                        continue

                    total_analyzed += 1
                    status, record = ImageRightsAuditService.get_field_audit_status(obj, f.name)

                    if status == 'missing':
                        total_missing += 1
                        if auto_create:
                            default_purpose, default_legal = ImageRightsAuditService.get_default_purpose_and_legal_basis(
                                model_cls._meta.model_name
                            )
                            meta = ImageRightsRecord.extract_file_metadata(file_attr)
                            
                            record = ImageRightsRecord.objects.create(
                                content_type=ct,
                                object_id=obj.pk,
                                image_field_name=f.name,
                                image_file_name=file_attr.name,
                                image_checksum=meta['checksum'],
                                image_width_px=meta['width'],
                                image_height_px=meta['height'],
                                file_size_kb=meta['size_kb'],
                                display_dimensions=f"{meta['width']}x{meta['height']}px ({meta['size_kb']} KB)" if meta['width'] else '',
                                usage_purpose=default_purpose,
                                legal_basis=default_legal,
                                work_title=str(obj)[:200],
                                usage_notes=f"Gerado automaticamente via audit_image_rights no modelo {model_cls._meta.model_name}."
                            )
                            total_created += 1
                            safe_obj_str = str(obj).encode('ascii', 'replace').decode('ascii')
                            self.stdout.write(self.style.SUCCESS(f"  [+] Criado registro para {safe_obj_str} [{f.name}]"))
                        else:
                            safe_obj_str = str(obj).encode('ascii', 'replace').decode('ascii')
                            self.stdout.write(self.style.WARNING(f"  [!] Sem registro: {safe_obj_str} [{f.name}]"))

                    elif record:
                        synced = ImageRightsAuditService.sync_file_metadata(record, file_attr)
                        if synced:
                            total_updated += 1
                            safe_rec_str = str(record).encode('ascii', 'replace').decode('ascii')
                            self.stdout.write(self.style.NOTICE(f"  [~] Metadados atualizados: {safe_rec_str}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"[OK] Rastreamento Concluido!"))
        self.stdout.write(f" Total de imagens analisadas: {total_analyzed}")
        self.stdout.write(f" Registros sem cadastro: {total_missing}")
        if auto_create:
            self.stdout.write(f" Novidades criadas: {total_created}")
        self.stdout.write(f" Metadados/dimensoes atualizados: {total_updated}")
        self.stdout.write("=" * 60 + "\n")



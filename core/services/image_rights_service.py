# core/services/image_rights_service.py
"""
Serviço para verificação de procedência de imagens, cálculo de badges de auditoria 🟢 🟡 🔴 ⚠️,
detecção de troca por Checksum (SHA-256) e mapa de conformidade corporativo por modelo.
"""

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import format_html

from core.models.image_rights import ImageRightsRecord


class ImageRightsAuditService:
    """
    Serviço central de auxílio e auditoria de direitos de imagens para admins e mapa de conformidade.
    """

    DEFAULT_MODEL_PURPOSES = {
        'book': ('review_debate', 'fair_use_art46'),
        'author': ('author_bio', 'fair_use_art46'),
        ('literaryuniverse', 'universecharacter', 'universelocation'): ('adaptation_info', 'fair_use_art46'),
        'event': ('event_publicity', 'express_consent'),
        ('banner', 'section'): ('institutional', 'own_production'),
        ('article', 'quiz'): ('review_debate', 'fair_use_art46'),
    }

    @classmethod
    def get_default_purpose_and_legal_basis(cls, model_name):
        """Retorna sugestões padrão de finalidade do uso e suporte jurídico com base no nome do modelo."""
        model_name = model_name.lower()
        for key, value in cls.DEFAULT_MODEL_PURPOSES.items():
            if isinstance(key, tuple) and model_name in key:
                return value
            elif isinstance(key, str) and model_name == key:
                return value
        return ('other', 'fair_use_art46')

    @classmethod
    def sync_file_metadata(cls, rights_record, file_attr):
        """Sincroniza automaticamente dimensões, peso em KB e checksum do arquivo no registro."""
        if not rights_record or not file_attr:
            return False

        meta = ImageRightsRecord.extract_file_metadata(file_attr)
        updated = False

        if meta['checksum'] and rights_record.image_checksum != meta['checksum']:
            rights_record.image_checksum = meta['checksum']
            updated = True

        if meta['width'] and rights_record.image_width_px != meta['width']:
            rights_record.image_width_px = meta['width']
            rights_record.image_height_px = meta['height']
            updated = True

        if meta['size_kb'] and rights_record.file_size_kb != meta['size_kb']:
            rights_record.file_size_kb = meta['size_kb']
            updated = True

        if meta['width'] and meta['height']:
            dim_str = f"{meta['width']}x{meta['height']}px ({meta['size_kb']} KB)"
            if rights_record.display_dimensions != dim_str:
                rights_record.display_dimensions = dim_str
                updated = True

        if updated:
            rights_record.save()

        return updated

    @classmethod
    def get_field_audit_status(cls, obj, field_name):
        """
        Retorna o estado da auditoria de um determinado campo de imagem em um objeto.
        - 'regularized': 🟢 Registro completo e consistente
        - 'pending': 🟡 Registro existente, mas com informações incompletas
        - 'missing': 🔴 Existe imagem, porém nenhum ImageRightsRecord correspondente
        - 'divergent': ⚠️ Checksum diferente da imagem cadastrada originalmente
        - 'no_image': None (sem imagem enviada no campo)
        """
        if not obj or not getattr(obj, 'pk', None):
            return 'no_image', None

        file_attr = getattr(obj, field_name, None)
        if not file_attr or not hasattr(file_attr, 'name') or not file_attr.name:
            return 'no_image', None

        ct = ContentType.objects.get_for_model(obj)
        rights_record = ImageRightsRecord.objects.filter(
            content_type=ct,
            object_id=obj.pk,
            image_field_name=field_name
        ).first()

        if not rights_record:
            return 'missing', None

        # Sincronizar metadados do arquivo se necessário
        if file_attr:
            cls.sync_file_metadata(rights_record, file_attr)

        # Verificar se o checksum do arquivo mudou
        if rights_record.image_checksum:
            current_checksum = ImageRightsRecord.calculate_file_checksum(file_attr)
            if current_checksum and current_checksum != rights_record.image_checksum:
                return 'divergent', rights_record

        # Verificar completude da licença e enquadramento
        if not rights_record.license_type:
            return 'pending', rights_record
        if rights_record.license_type == 'cc' and (not rights_record.license_url or not rights_record.source_url):
            return 'pending', rights_record

        return 'regularized', rights_record

    @classmethod
    def get_field_audit_badge_html(cls, obj, field_name):
        """Retorna a badge HTML formatada para exibição em formulários/listagens do admin."""
        status, record = cls.get_field_audit_status(obj, field_name)
        if status == 'no_image':
            return ''
        elif status == 'regularized':
            return format_html('<span style="background:#27ae60; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🟢 Regularizada</span>')
        elif status == 'pending':
            return format_html('<span style="background:#f39c12; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🟡 Pendente</span>')
        elif status == 'divergent':
            return format_html('<span style="background:#e67e22; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⚠️ Checksum Divergente</span>')
        else:
            return format_html('<span style="background:#c0392b; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🔴 Sem Registro</span>')

    @classmethod
    def audit_model_admin_save(cls, request, obj):
        """
        Executado no save_model dos admins principais.
        Verifica os campos de imagem e exibe avisos educativos não-bloqueantes.
        """
        if not obj or not obj.pk:
            return

        model_cls = obj.__class__

        for field in model_cls._meta.get_fields():
            if isinstance(field, (models.ImageField, models.FileField)):
                status, record = cls.get_field_audit_status(obj, field.name)
                if status == 'missing':
                    messages.warning(
                        request,
                        f"⚠️ Auditoria de Imagens: O campo '{field.verbose_name}' possui imagem enviada sem registro de procedência. Preencha na seção 'Direitos Autorais e Procedência'."
                    )
                elif status == 'divergent':
                    messages.warning(
                        request,
                        f"⚠️ Alerta Checksum: O arquivo do campo '{field.verbose_name}' foi alterado no disco. Atualize os direitos autorais deste ativo visual!"
                    )

    @classmethod
    def get_model_compliance_stats(cls, model_cls):
        """
        Calcula as estatísticas e a taxa percentual de conformidade de mídias para um modelo específico.
        """
        ct = ContentType.objects.get_for_model(model_cls)
        image_field_names = [
            f.name for f in model_cls._meta.get_fields()
            if isinstance(f, (models.ImageField, models.FileField))
        ]

        if not image_field_names:
            return {'total_images': 0, 'regularized': 0, 'pending': 0, 'missing': 0, 'divergent': 0, 'rate': 100.0}

        total_images = 0
        regularized = 0
        pending = 0
        missing = 0
        divergent = 0

        # Iterar sobre as instâncias do modelo que possuem arquivo
        for obj in model_cls.objects.all():
            for field_name in image_field_names:
                status, record = cls.get_field_audit_status(obj, field_name)
                if status != 'no_image':
                    total_images += 1
                    if status == 'regularized':
                        regularized += 1
                    elif status == 'pending':
                        pending += 1
                    elif status == 'divergent':
                        divergent += 1
                    elif status == 'missing':
                        missing += 1

        rate = round((regularized / total_images * 100), 1) if total_images > 0 else 100.0
        return {
            'model_name': model_cls._meta.verbose_name_plural.title(),
            'total_images': total_images,
            'regularized': regularized,
            'pending': pending,
            'missing': missing,
            'divergent': divergent,
            'rate': rate
        }


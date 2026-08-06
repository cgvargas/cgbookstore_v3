# core/services/image_rights_service.py
"""
Serviço para verificação de procedência de imagens, detecção de troca por Checksum (SHA-256)
e utilitários para avisos não-bloqueantes no Django Admin.
"""

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models.image_rights import ImageRightsRecord


class ImageRightsAuditService:
    """
    Serviço central de auxílio e auditoria de direitos de imagens para admins.
    """

    @classmethod
    def audit_model_admin_save(cls, request, obj):
        """
        Executado no save_model dos admins principais (Book, Author, LiteraryUniverse, Banner, etc.).
        Verifica os campos de imagem do objeto:
        1. Alerta se houver imagem sem registro de direitos autorais.
        2. Detecta se a imagem mudou comparando o Checksum SHA-256 e alerta sobre a necessidade de reauditoria.
        """
        if not obj or not obj.pk:
            return

        ct = ContentType.objects.get_for_model(obj)
        model_cls = obj.__class__

        for field in model_cls._meta.get_fields():
            if isinstance(field, (models.ImageField, models.FileField)):
                file_attr = getattr(obj, field.name, None)
                if file_attr and hasattr(file_attr, 'name') and file_attr.name:
                    # Tentar buscar o registro de direitos autorais existente
                    rights_record = ImageRightsRecord.objects.filter(
                        content_type=ct,
                        object_id=obj.pk,
                        image_field_name=field.name
                    ).first()

                    if not rights_record:
                        messages.warning(
                            request,
                            f"⚠️ Auditoria de Imagens: O campo de imagem '{field.verbose_name}' ({field.name}) possui arquivo cadastrado, mas NÃO tem registro de procedência/direitos autorais. Adicione na seção 'Direitos Autorais e Procedência'."
                        )
                    else:
                        # Verificar se o arquivo mudou via Checksum SHA-256
                        if rights_record.image_checksum:
                            current_checksum = ImageRightsRecord.calculate_file_checksum(file_attr)
                            if current_checksum and current_checksum != rights_record.image_checksum:
                                messages.warning(
                                    request,
                                    f"⚠️ Alerta de Substituição de Arquivo: O arquivo do campo '{field.verbose_name}' foi alterado (Checksum SHA-256 divergente do auditado). Por favor, revise e atualize os direitos autorais deste ativo visual!"
                                )

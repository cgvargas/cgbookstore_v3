# core/services/image_rights_history_service.py
"""
Serviço Centralizado para Registro da Trilha Histórica de Auditoria de Direitos Autorais (ImageRightsAuditLog).
Garante atomicidade, higienização estrita contra vazamento de PII / caminhos de documentos privados,
e proteção contra duplicações consecutivas (deduplicação arquitetural).
"""

import logging
from django.db import transaction
from django.utils import timezone
from core.models.image_rights_audit_log import ImageRightsAuditLog

logger = logging.getLogger(__name__)


class ImageRightsHistoryService:
    """
    Serviço central de registro da trilha de auditoria append-only.
    Todos os eventos históricos devem ser gerados através desta classe.
    """

    AUDITED_FIELDS_CONFIG = {
        'creator_name': {
            'event_type': 'creator_changed',
            'label': 'Autor/Criador da Imagem',
        },
        'rights_holder_name': {
            'event_type': 'rights_holder_changed',
            'label': 'Titular dos Direitos',
        },
        'licensor_name': {
            'event_type': 'licensor_changed',
            'label': 'Licenciante / Entidade Administradora',
        },
        'source_url': {
            'event_type': 'source_changed',
            'label': 'Fonte Original da Imagem',
        },
        'license_type': {
            'event_type': 'license_changed',
            'label': 'Regime de Licença / Procedência',
        },
        'legal_basis': {
            'event_type': 'legal_basis_changed',
            'label': 'Fundamento Jurídico',
        },
        'audit_status': {
            'event_type': 'audit_status_changed',
            'label': 'Status de Auditoria e Governança',
        },
        'public_display_allowed': {
            'event_type': 'public_display_changed',
            'label': 'Permissão de Exibição Pública',
        },
        'license_url': {
            'event_type': 'record_updated',
            'label': 'URL Oficial da Licença',
        },
        'usage_purpose': {
            'event_type': 'record_updated',
            'label': 'Finalidade do Uso',
        },
        'work_title': {
            'event_type': 'record_updated',
            'label': 'Título da Obra Visual',
        },
        'credit_name': {
            'event_type': 'record_updated',
            'label': 'Crédito Legado / Atribuição',
        },
        'is_ai_generated': {
            'event_type': 'record_updated',
            'label': 'Gerada por Inteligência Artificial',
        },
        'display_dimensions': {
            'event_type': 'record_updated',
            'label': 'Dimensões de Exibição',
        },
        'permission_document': {
            'event_type': 'permission_document_changed',
            'label': 'Documento Comprobatório',
        },
        'usage_notes': {
            'event_type': 'record_updated',
            'label': 'Observações Internas',
        },
    }

    @classmethod
    def _sanitize_field_value(cls, field_name, value):
        """
        Garante que valores armazenados no log não contenham dados sensíveis,
        caminhos confidenciais de arquivos ou textos longos de notas internas.
        """
        if value is None:
            return ''

        # Campo booleano
        if isinstance(value, bool):
            return 'Sim' if value else 'Não'

        # Documento privado: NUNCA armazenar caminho ou link
        if field_name == 'permission_document':
            if bool(value):
                return 'Documento comprobatório anexado'
            return 'Nenhum documento'

        # Observações de uso internas: NUNCA gravar o texto integral no histórico
        if field_name == 'usage_notes':
            if str(value).strip():
                return 'Observações administrativas cadastradas'
            return 'Sem observações'

        val_str = str(value).strip()
        # Truncar com segurança para caber em max_length=500
        if len(val_str) > 490:
            return val_str[:487] + '...'
        return val_str

    @classmethod
    def log_event(
        cls,
        image_rights_record,
        event_type,
        description,
        performed_by=None,
        source='service',
        field_name='',
        old_value='',
        new_value='',
        takedown_request=None,
        metadata=None,
        suppress_duplicate=False
    ):
        """
        Cria uma entrada imutável no log de auditoria dentro de transação atômica.
        """
        if not image_rights_record or not image_rights_record.pk:
            logger.warning("Tentativa de criar ImageRightsAuditLog sem ImageRightsRecord persistido.")
            return None

        clean_old = cls._sanitize_field_value(field_name, old_value)
        clean_new = cls._sanitize_field_value(field_name, new_value)
        meta = metadata if metadata is not None else {}

        # Proteção contra duplicatas consecutivas idênticas se solicitado
        if suppress_duplicate:
            last_log = image_rights_record.audit_logs.filter(
                event_type=event_type,
                field_name=field_name
            ).order_by('-created_at', '-id').first()

            if last_log and last_log.old_value == clean_old and last_log.new_value == clean_new:
                # Evita registrar o mesmo alerta consecutivamente
                return last_log

        with transaction.atomic():
            log_entry = ImageRightsAuditLog.objects.create(
                image_rights_record=image_rights_record,
                event_type=event_type,
                description=description[:500],
                performed_by=performed_by,
                source=source,
                field_name=field_name[:100] if field_name else '',
                old_value=clean_old,
                new_value=clean_new,
                takedown_request=takedown_request,
                metadata=meta
            )
            return log_entry

    @classmethod
    def log_record_created(cls, record, performed_by=None, source='admin', metadata=None):
        """Registra a criação de um novo registro de direitos autorais."""
        desc = f"Registro de direitos autorais criado para o campo '{record.image_field_name}'."
        return cls.log_event(
            image_rights_record=record,
            event_type='record_created',
            description=desc,
            performed_by=performed_by,
            source=source,
            new_value=f"Status: {record.get_audit_status_display()} | Licença: {record.get_license_type_display() or 'Não informada'}",
            metadata=metadata
        )

    @classmethod
    def log_record_changes(cls, record, old_instance, performed_by=None, source='admin'):
        """
        Compara a instância atual do ImageRightsRecord com os valores anteriores
        e registra eventos específicos para cada campo juridicamente relevante alterado.
        """
        if not old_instance or not record:
            return []

        logs_created = []

        for field_name, config in cls.AUDITED_FIELDS_CONFIG.items():
            old_val = getattr(old_instance, field_name, None)
            new_val = getattr(record, field_name, None)

            # Para FileFields, verificar presença/mudança
            if field_name == 'permission_document':
                old_has = bool(old_val)
                new_has = bool(new_val)
                if old_has != new_has or (old_has and new_has and old_val.name != new_val.name):
                    if not old_has and new_has:
                        desc = "Documento comprobatório adicionado."
                    elif old_has and not new_has:
                        desc = "Documento comprobatório removido."
                    else:
                        desc = "Documento comprobatório substituído."
                    
                    log = cls.log_event(
                        image_rights_record=record,
                        event_type=config['event_type'],
                        description=desc,
                        performed_by=performed_by,
                        source=source,
                        field_name=field_name,
                        old_value='Sim' if old_has else 'Não',
                        new_value='Sim' if new_has else 'Não',
                    )
                    logs_created.append(log)
                continue

            # Para campos normais
            if old_val != new_val:
                label = config['label']
                event_type = config['event_type']

                # Formatador para escolhas
                old_display = old_val
                new_display = new_val
                if field_name == 'audit_status':
                    old_dict = dict(record.AUDIT_STATUS_CHOICES)
                    new_dict = dict(record.AUDIT_STATUS_CHOICES)
                    old_display = old_dict.get(old_val, old_val)
                    new_display = new_dict.get(new_val, new_val)
                elif field_name == 'license_type':
                    license_dict = dict(record.LICENSE_CHOICES)
                    old_display = license_dict.get(old_val, old_val or 'Não informada')
                    new_display = license_dict.get(new_val, new_val or 'Não informada')
                elif field_name == 'legal_basis':
                    basis_dict = dict(record.LEGAL_BASIS_CHOICES)
                    old_display = basis_dict.get(old_val, old_val or 'Não informado')
                    new_display = basis_dict.get(new_val, new_val or 'Não informado')

                if field_name == 'usage_notes':
                    desc = "Observações administrativas internas alteradas."
                else:
                    desc = f"{label} alterado de '{cls._sanitize_field_value(field_name, old_display)}' para '{cls._sanitize_field_value(field_name, new_display)}'."

                log = cls.log_event(
                    image_rights_record=record,
                    event_type=event_type,
                    description=desc,
                    performed_by=performed_by,
                    source=source,
                    field_name=field_name,
                    old_value=old_display,
                    new_value=new_display
                )
                logs_created.append(log)

        return logs_created

    @classmethod
    def log_suspension(cls, record, performed_by=None, source='service', notes=None, takedown_request=None):
        """Registra a suspensão preventiva de exibição pública de uma imagem."""
        desc = "Exibição pública suspensa preventivamente."
        if takedown_request:
            desc = f"Exibição pública suspensa preventivamente em razão da contestação #{takedown_request.pk}."

        return cls.log_event(
            image_rights_record=record,
            event_type='image_suspended',
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='public_display_allowed',
            old_value='Permitida',
            new_value='Bloqueada / Suspensa',
            takedown_request=takedown_request,
            metadata={'action': 'preventive_suspension'}
        )

    @classmethod
    def log_restoration(cls, record, performed_by=None, source='service', takedown_request=None):
        """Registra a restauração de exibição pública de uma imagem."""
        desc = "Exibição pública da imagem restaurada após verificação de conformidade."
        if takedown_request:
            desc = f"Exibição pública restaurada após análise da contestação #{takedown_request.pk}."

        return cls.log_event(
            image_rights_record=record,
            event_type='image_restored',
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='public_display_allowed',
            old_value='Bloqueada / Suspensa',
            new_value='Permitida',
            takedown_request=takedown_request,
            metadata={'action': 'asset_restoration'}
        )

    @classmethod
    def log_takedown_received(cls, takedown, performed_by=None, source='system'):
        """
        Registra o recebimento formal de uma contestação/takedown.
        NÃO inclui email, documentos probatórios ou texto confidencial.
        """
        record = takedown.image_rights_record
        if not record:
            return None

        # Dados estruturados e seguros: papel do reclamante e organização
        role_display = takedown.get_claimant_role_display()
        org_info = f" ({takedown.claimant_organization})" if takedown.claimant_organization else ""
        desc = f"Notificação/Contestação #{takedown.pk} recebida de {role_display}{org_info}."

        return cls.log_event(
            image_rights_record=record,
            event_type='takedown_received',
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='takedown_status',
            old_value='',
            new_value=takedown.get_status_display(),
            takedown_request=takedown,
            metadata={
                'takedown_id': takedown.pk,
                'claimant_role': takedown.claimant_role,
            }
        )

    @classmethod
    def log_takedown_status_changed(cls, takedown, old_status, new_status, performed_by=None, source='admin'):
        """Registra a alteração de status de uma contestação."""
        record = takedown.image_rights_record
        if not record:
            return None

        status_dict = dict(takedown.STATUS_CHOICES)
        old_label = status_dict.get(old_status, old_status)
        new_label = status_dict.get(new_status, new_status)

        desc = f"Status da contestação #{takedown.pk} alterado de '{old_label}' para '{new_label}'."

        return cls.log_event(
            image_rights_record=record,
            event_type='takedown_status_changed',
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='takedown_status',
            old_value=old_label,
            new_value=new_label,
            takedown_request=takedown,
            metadata={
                'takedown_id': takedown.pk,
                'old_status': old_status,
                'new_status': new_status
            }
        )

    @classmethod
    def log_takedown_resolution(cls, takedown, resolution_type, performed_by=None, source='service', notes=''):
        """
        Registra a conclusão formal de uma contestação (keep ou remove).
        """
        record = takedown.image_rights_record
        if not record:
            return None

        if resolution_type == 'remove':
            event_type = 'takedown_resolved_removed'
            desc = f"Contestação #{takedown.pk} concluída com RETIRADA DA IMAGEM. Exibição pública bloqueada."
            new_val = 'Resolvida — Imagem Retirada'
        else:
            event_type = 'takedown_resolved_keep'
            desc = f"Contestação #{takedown.pk} concluída com MANUTENÇÃO DO USO da imagem."
            new_val = 'Resolvida — Uso Mantido'

        return cls.log_event(
            image_rights_record=record,
            event_type=event_type,
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='takedown_status',
            old_value='Em Análise',
            new_value=new_val,
            takedown_request=takedown,
            metadata={
                'takedown_id': takedown.pk,
                'resolution_type': resolution_type,
            }
        )

    @classmethod
    def log_integrity_divergence(cls, record, expected_checksum, detected_checksum, source='command'):
        """
        Registra a detecção de divergência de integridade (checksum incompatível).
        Possui proteção contra duplicação de alertas consecutivos idênticos.
        """
        desc = f"Divergência de integridade detectada no arquivo de imagem do campo '{record.image_field_name}'."
        return cls.log_event(
            image_rights_record=record,
            event_type='integrity_divergence_detected',
            description=desc,
            performed_by=None,
            source=source,
            field_name='image_checksum',
            old_value=expected_checksum[:16] + '...' if expected_checksum else 'Não registrado',
            new_value=detected_checksum[:16] + '...' if detected_checksum else 'Não calculado',
            suppress_duplicate=True,
            metadata={
                'expected_checksum': expected_checksum,
                'detected_checksum': detected_checksum,
            }
        )

    @classmethod
    def log_checksum_updated(cls, record, old_checksum, new_checksum, performed_by=None, source='command'):
        """
        Registra a atualização legítima de checksum SHA-256 e metadados técnicos.
        """
        desc = f"Checksum SHA-256 da imagem recalculado/atualizado para o campo '{record.image_field_name}'."
        return cls.log_event(
            image_rights_record=record,
            event_type='checksum_updated',
            description=desc,
            performed_by=performed_by,
            source=source,
            field_name='image_checksum',
            old_value=old_checksum[:16] + '...' if old_checksum else 'Não registrado',
            new_value=new_checksum[:16] + '...' if new_checksum else 'Não calculado',
            suppress_duplicate=True,
            metadata={
                'old_checksum': old_checksum,
                'new_checksum': new_checksum,
            }
        )

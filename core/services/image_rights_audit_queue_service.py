# core/services/image_rights_audit_queue_service.py
"""
Serviço Centralizado de Fila Inteligente e Priorização de Auditoria de Direitos Autorais de Imagens.

DIRETRIZ CENTRAL DE GOVERNANÇA (FASE 2):
- AUTOMAÇÃO OPERACIONAL ≠ DECISÃO JURÍDICA AUTOMÁTICA
- O serviço calcula score determinístico (0-100), prioridades e motivos explicáveis para organizar
  a ordem de trabalho do administrador.
- NENHUMA imagem é regularizada, aprovada ou restaurada automaticamente por este serviço.
- O cálculo de score é 100% livre de efeitos colaterais: não altera modelos e não gera logs de auditoria.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from django.db.models import Q, Count, Exists, OuterRef, Prefetch
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from core.models.image_rights import ImageRightsRecord
from core.models.copyright_takedown import CopyrightTakedownRequest
from core.models.image_rights_audit_log import ImageRightsAuditLog

logger = logging.getLogger(__name__)


@dataclass
class AuditQueueItem:
    """Estrutura estruturada e imutável representando um item avaliado na fila de auditoria."""
    record: ImageRightsRecord
    priority_level: str  # 'critical', 'high', 'medium', 'low'
    priority_level_display: str  # 'Crítica', 'Alta', 'Média', 'Baixa'
    priority_score: int  # 0 a 100
    reasons: List[str] = field(default_factory=list)
    suggested_action: str = "Realizar auditoria inicial"
    needs_review: bool = True
    has_active_takedown: bool = False
    has_integrity_divergence: bool = False
    can_display_publicly: bool = True
    related_object_title: str = ""
    related_object_admin_url: str = ""
    edit_record_url: str = ""
    takedown_url: str = ""


class ImageRightsAuditQueueService:
    """
    Serviço central que orquestra a Fila Operacional Inteligente de Auditoria de Imagens.
    """

    # Níveis de Prioridade
    PRIORITY_CRITICAL = 'critical'
    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'

    PRIORITY_DISPLAY_MAP = {
        PRIORITY_CRITICAL: 'Crítica',
        PRIORITY_HIGH: 'Alta',
        PRIORITY_MEDIUM: 'Média',
        PRIORITY_LOW: 'Baixa',
    }

    # Ações Sugeridas Padronizadas
    ACTION_REVIEW_TAKEDOWN = "Revisar contestação"
    ACTION_VERIFY_DOCUMENTATION = "Verificar documentação"
    ACTION_IDENTIFY_PROVENANCE = "Identificar procedência"
    ACTION_IDENTIFY_CREATOR = "Identificar criador"
    ACTION_VERIFY_LICENSE = "Verificar licença"
    ACTION_REVIEW_DIVERGENCE = "Revisar divergência de integridade"
    ACTION_INITIAL_AUDIT = "Realizar auditoria inicial"
    ACTION_NO_URGENT_ACTION = "Nenhuma ação urgente"

    @classmethod
    def evaluate_record(cls, record: ImageRightsRecord) -> AuditQueueItem:
        """
        Avalia deterministicamente um ImageRightsRecord e retorna seu score, prioridade,
        motivos e ação recomendada, sem alterar o banco de dados e sem gerar histórico.
        """
        score = 0
        reasons = []
        suggested_action = cls.ACTION_INITIAL_AUDIT
        has_active_takedown = False
        has_integrity_divergence = False

        # 1. Avaliar Contestações de Takedown
        # Reutiliza prefetch se disponível ou faz query pontual
        if hasattr(record, 'prefetched_takedowns'):
            takedowns = record.prefetched_takedowns
        elif hasattr(record, '_prefetched_objects_cache') and 'takedown_requests' in record._prefetched_objects_cache:
            takedowns = list(record.takedown_requests.all())
        else:
            takedowns = list(record.takedown_requests.all())

        active_takedowns = [t for t in takedowns if t.status in ['received', 'under_review', 'awaiting_information', 'temporarily_suspended']]
        resolved_removed_takedowns = [t for t in takedowns if t.status == 'resolved_removed']

        if active_takedowns:
            has_active_takedown = True
            score += 55
            reasons.append("Contestação formal ou notificação de takedown ativa em andamento.")
            suggested_action = cls.ACTION_REVIEW_TAKEDOWN
        elif record.audit_status == 'contested':
            score += 45
            reasons.append("Registro marcado formalmente como sob contestação judicial/extrajudicial.")
            suggested_action = cls.ACTION_REVIEW_TAKEDOWN

        # 2. Avaliar Divergência Técnica de Integridade
        # Verifica se há divergência no log ou no arquivo atual
        if hasattr(record, 'has_logged_divergence') and record.has_logged_divergence:
            has_integrity_divergence = True
            score += 35
            reasons.append("Divergência de integridade registrada em histórico técnico.")
            if not active_takedowns:
                suggested_action = cls.ACTION_REVIEW_DIVERGENCE
        elif record.image_checksum and record.content_object:
            file_attr = getattr(record.content_object, record.image_field_name, None)
            if file_attr and hasattr(file_attr, 'name') and file_attr.name:
                try:
                    current_chk = ImageRightsRecord.calculate_file_checksum(file_attr)
                    if current_chk and current_chk != record.image_checksum:
                        has_integrity_divergence = True
                        score += 35
                        reasons.append("Divergência de integridade: o arquivo físico foi alterado após o cadastro.")
                        if not active_takedowns:
                            suggested_action = cls.ACTION_REVIEW_DIVERGENCE
                except Exception:
                    pass

        # 3. Avaliar Estado de Governança (audit_status) e Exposição Pública
        if record.audit_status == 'not_audited':
            if record.public_display_allowed:
                score += 35
                reasons.append("Imagem em exibição pública sem conclusão de auditoria administrativa.")
            else:
                score += 20
                reasons.append("Imagem não auditada (exibição atualmente desabilitada).")
            if not active_takedowns and not has_integrity_divergence:
                suggested_action = cls.ACTION_INITIAL_AUDIT

        elif record.audit_status == 'pending':
            score += 25
            reasons.append("Auditoria administrativa pendente de comprovação documental ou esclarecimento.")
            if not active_takedowns and not has_integrity_divergence:
                suggested_action = cls.ACTION_VERIFY_DOCUMENTATION

        elif record.audit_status == 'under_review':
            score += 20
            reasons.append("Ativo visual em processo de análise de conformidade.")
            if not active_takedowns and not has_integrity_divergence:
                suggested_action = cls.ACTION_VERIFY_DOCUMENTATION

        elif record.audit_status == 'restricted':
            if has_active_takedown:
                score += 40
                reasons.append("Imagem preventivamente suspensa aguardando desfecho de contestação.")
                suggested_action = cls.ACTION_REVIEW_TAKEDOWN
            elif resolved_removed_takedowns and not record.public_display_allowed:
                # Caso encerrado e resolvido com remoção
                score += 10
                reasons.append("Uso restrito definitivo: contestação encerrada com remoção.")
                suggested_action = cls.ACTION_NO_URGENT_ACTION
            else:
                score += 25
                reasons.append("Uso restrito ou suspenso administrativamente.")
                suggested_action = cls.ACTION_VERIFY_DOCUMENTATION

        elif record.audit_status == 'regularized':
            if has_active_takedown or has_integrity_divergence:
                score += 30
                reasons.append("Registro anteriormente regularizado apresentou novo evento crítico.")
            else:
                # Registro regularizado limpo
                score = 0
                reasons.append("Ativo regularizado documentalmente e tecnicamente consistente.")
                suggested_action = cls.ACTION_NO_URGENT_ACTION

        # Identificar casos finais/encerrados que não precisam de pontuação adicional
        is_resolved_final = (
            record.audit_status == 'restricted' 
            and bool(resolved_removed_takedowns) 
            and not record.public_display_allowed 
            and not has_active_takedown 
            and not has_integrity_divergence
        )
        is_clean_regularized = (
            record.audit_status == 'regularized' 
            and not has_active_takedown 
            and not has_integrity_divergence
        )

        # 4. Avaliar Procedência Técnica e Metadados para registros sob auditoria ativa
        if not is_clean_regularized and not is_resolved_final:
            if record.is_auto_imported and record.audit_status == 'not_audited':
                score += 15
                prov_name = record.get_provenance_provider_display() if record.provenance_provider else 'fonte externa'
                reasons.append(f"Importação automática via [{prov_name}] pendente de homologação humana.")

            if not record.provenance_provider and not record.source_url and not record.is_ai_generated:
                score += 15
                reasons.append("Procedência técnica não informada (sem provedor e sem URL de origem).")
                if suggested_action == cls.ACTION_INITIAL_AUDIT:
                    suggested_action = cls.ACTION_IDENTIFY_PROVENANCE

            # 5. Avaliar Atribuição (Criador / Titular)
            if not record.is_ai_generated and record.license_type != 'own':
                if not record.creator_name and not record.credit_name:
                    score += 10
                    reasons.append("Criador/Autor da imagem não identificado nos metadados.")
                    if suggested_action == cls.ACTION_INITIAL_AUDIT:
                        suggested_action = cls.ACTION_IDENTIFY_CREATOR

                if not record.rights_holder_name and record.license_type not in ['public_domain', 'cc']:
                    score += 10
                    reasons.append("Titular patrimonial dos direitos autorais não especificado.")

        # 6. Avaliar Licença e Documento
        if not is_clean_regularized and not is_resolved_final:
            # Se for produção própria interna ou IA gerada internamente, não exige licença externa
            is_internal_or_ai = record.is_ai_generated or record.legal_basis == 'own_production' or record.license_type == 'own'
            
            if not record.license_type and not record.legal_basis and not is_internal_or_ai:
                score += 10
                reasons.append("Regime de licença e fundamento jurídico não informados.")
                if suggested_action in [cls.ACTION_INITIAL_AUDIT, cls.ACTION_IDENTIFY_CREATOR]:
                    suggested_action = cls.ACTION_VERIFY_LICENSE

            if record.license_type == 'licensed' and not record.permission_document and not record.usage_notes:
                score += 15
                reasons.append("Imagem declarada como licenciada sem documento comprobatório anexado.")
                suggested_action = cls.ACTION_VERIFY_DOCUMENTATION

            if record.legal_basis == 'express_consent' and not record.permission_document:
                score += 15
                reasons.append("Autorização expressa declarada sem contrato/anuência anexada.")
                suggested_action = cls.ACTION_VERIFY_DOCUMENTATION

            # 7. Ajuste de Exposição Pública
            if record.public_display_allowed and score > 0:
                score += 5

        # 8. Normalizar Score e Determinar Nível Operacional
        if has_active_takedown:
            # Contestações ativas sempre têm prioridade crítica e score mínimo de 90
            final_score = max(90, min(100, score))
            priority_level = cls.PRIORITY_CRITICAL
        else:
            final_score = max(0, min(100, score))
            if final_score >= 80:
                priority_level = cls.PRIORITY_CRITICAL
            elif final_score >= 55:
                priority_level = cls.PRIORITY_HIGH
            elif final_score >= 30:
                priority_level = cls.PRIORITY_MEDIUM
            else:
                priority_level = cls.PRIORITY_LOW

            # REGRA OPERACIONAL EXPLÍCITA (FASE 2):
            # Imagem pública não auditada (not_audited + public_display_allowed=True)
            # deve ter prioridade operacional MÍNIMA 'high', mesmo sem importação externa ou outros agravantes.
            if record.audit_status == 'not_audited' and record.public_display_allowed:
                if priority_level in [cls.PRIORITY_LOW, cls.PRIORITY_MEDIUM]:
                    priority_level = cls.PRIORITY_HIGH

        # 9. Determinar se precisa de revisão (needs_review)
        # needs_review é False apenas para regularizados sem pendências ou restritos finais resolvidos
        needs_review = True
        if record.audit_status == 'regularized' and not has_active_takedown and not has_integrity_divergence:
            needs_review = False
        elif record.audit_status == 'restricted' and not has_active_takedown and not record.public_display_allowed and resolved_removed_takedowns:
            needs_review = False

        # Título do objeto relacionado
        related_title = ""
        related_admin_url = ""
        if record.content_object:
            related_title = str(record.content_object)
            try:
                app_label = record.content_type.app_label
                model_name = record.content_type.model
                related_admin_url = reverse(f'admin:{app_label}_{model_name}_change', args=[record.object_id])
            except Exception:
                related_admin_url = ""

        edit_record_url = ""
        try:
            edit_record_url = reverse('admin:core_imagerightsrecord_change', args=[record.pk])
        except Exception:
            pass

        takedown_url = ""
        if active_takedowns:
            try:
                takedown_url = reverse('admin:core_copyrighttakedownrequest_change', args=[active_takedowns[0].pk])
            except Exception:
                pass

        return AuditQueueItem(
            record=record,
            priority_level=priority_level,
            priority_level_display=cls.PRIORITY_DISPLAY_MAP.get(priority_level, 'Baixa'),
            priority_score=final_score,
            reasons=reasons,
            suggested_action=suggested_action,
            needs_review=needs_review,
            has_active_takedown=has_active_takedown,
            has_integrity_divergence=has_integrity_divergence,
            can_display_publicly=record.can_display_publicly,
            related_object_title=related_title,
            related_object_admin_url=related_admin_url,
            edit_record_url=edit_record_url,
            takedown_url=takedown_url
        )

    @classmethod
    def get_queue_queryset(cls, filters: Optional[Dict[str, Any]] = None, search_query: str = '', order_by: str = '-priority') -> List[AuditQueueItem]:
        """
        Retorna a lista completa de itens avaliados para a fila de auditoria com otimização
        anti N+1 queries.
        """
        filters = filters or {}
        qs = ImageRightsRecord.objects.select_related(
            'content_type',
            'created_by'
        ).prefetch_related(
            Prefetch('takedown_requests', queryset=CopyrightTakedownRequest.objects.all(), to_attr='prefetched_takedowns')
        ).annotate(
            has_logged_divergence=Exists(
                ImageRightsAuditLog.objects.filter(
                    image_rights_record=OuterRef('pk'),
                    event_type='integrity_divergence_detected'
                )
            )
        )

        # Filtro de Estado de Auditoria
        audit_status = filters.get('audit_status')
        if audit_status:
            qs = qs.filter(audit_status=audit_status)

        # Filtro de Exibição Pública
        public_display = filters.get('public_display')
        if public_display in ['true', 'True', True]:
            qs = qs.filter(public_display_allowed=True)
        elif public_display in ['false', 'False', False]:
            qs = qs.filter(public_display_allowed=False)

        # Filtro de Provedor
        provider = filters.get('provider')
        if provider:
            qs = qs.filter(provenance_provider=provider)

        # Filtro de Origem Automática
        is_auto = filters.get('is_auto_imported')
        if is_auto in ['true', 'True', True]:
            qs = qs.filter(is_auto_imported=True)
        elif is_auto in ['false', 'False', False]:
            qs = qs.filter(is_auto_imported=False)

        # Filtro de Documento Comprobatório
        has_document = filters.get('has_document')
        if has_document in ['true', 'True', True]:
            qs = qs.exclude(permission_document='')
        elif has_document in ['false', 'False', False]:
            qs = qs.filter(permission_document='')

        # Filtro de Criador Informado
        has_creator = filters.get('has_creator')
        if has_creator in ['true', 'True', True]:
            qs = qs.exclude(creator_name='')
        elif has_creator in ['false', 'False', False]:
            qs = qs.filter(creator_name='')

        # Filtro de Titular Informado
        has_rights_holder = filters.get('has_rights_holder')
        if has_rights_holder in ['true', 'True', True]:
            qs = qs.exclude(rights_holder_name='')
        elif has_rights_holder in ['false', 'False', False]:
            qs = qs.filter(rights_holder_name='')

        # Filtro de Licença Informada
        has_license = filters.get('has_license')
        if has_license in ['true', 'True', True]:
            qs = qs.exclude(license_type='')
        elif has_license in ['false', 'False', False]:
            qs = qs.filter(license_type='')

        # Filtro de Tipo de Conteúdo (Model de Origem)
        content_type_id = filters.get('content_type_id')
        if content_type_id:
            qs = qs.filter(content_type_id=content_type_id)

        # Filtro de Campo de Imagem
        image_field_name = filters.get('image_field_name')
        if image_field_name:
            qs = qs.filter(image_field_name=image_field_name)

        # Busca Segura (Sem expor PII de reclamantes ou documentos confidenciais)
        if search_query:
            sq = search_query.strip()
            search_filter = (
                Q(creator_name__icontains=sq) |
                Q(rights_holder_name__icontains=sq) |
                Q(image_file_name__icontains=sq) |
                Q(provider_asset_id__icontains=sq) |
                Q(source_url__icontains=sq)
            )
            if sq.isdigit():
                search_filter |= Q(object_id=int(sq)) | Q(pk=int(sq))
            qs = qs.filter(search_filter)

        # Avaliar cada registro deterministicamente
        evaluated_items: List[AuditQueueItem] = []
        for record in qs:
            item = cls.evaluate_record(record)
            evaluated_items.append(item)

        # Filtro pós-avaliação por Prioridade
        priority_filter = filters.get('priority')
        if priority_filter:
            evaluated_items = [it for it in evaluated_items if it.priority_level == priority_filter]

        # Filtro de Takedown Ativo
        has_takedown = filters.get('has_takedown')
        if has_takedown in ['true', 'True', True]:
            evaluated_items = [it for it in evaluated_items if it.has_active_takedown]
        elif has_takedown in ['false', 'False', False]:
            evaluated_items = [it for it in evaluated_items if not it.has_active_takedown]

        # Filtro de Divergência
        has_divergence = filters.get('has_divergence')
        if has_divergence in ['true', 'True', True]:
            evaluated_items = [it for it in evaluated_items if it.has_integrity_divergence]
        elif has_divergence in ['false', 'False', False]:
            evaluated_items = [it for it in evaluated_items if not it.has_integrity_divergence]

        # Filtro padrão: apenas itens que precisam de revisão (needs_review=True), a menos que explicitamente solicitado
        show_all = filters.get('show_all')
        if not show_all and not audit_status:
            evaluated_items = [it for it in evaluated_items if it.needs_review]

        # Ordenação Determinística
        if order_by == '-score' or order_by == '-priority':
            # 1. Score decrescente, 2. Mais antigos criados (created_at crescente)
            evaluated_items.sort(key=lambda x: (-x.priority_score, x.record.created_at))
        elif order_by == 'score' or order_by == 'priority':
            evaluated_items.sort(key=lambda x: (x.priority_score, x.record.created_at))
        elif order_by == '-created_at':
            evaluated_items.sort(key=lambda x: x.record.created_at, reverse=True)
        elif order_by == 'created_at':
            evaluated_items.sort(key=lambda x: x.record.created_at)
        elif order_by == 'status':
            evaluated_items.sort(key=lambda x: (x.record.audit_status, -x.priority_score))
        elif order_by == 'provider':
            evaluated_items.sort(key=lambda x: (x.record.provenance_provider or 'zzz', -x.priority_score))
        else:
            # Padrão: prioridade/score decrescente
            evaluated_items.sort(key=lambda x: (-x.priority_score, x.record.created_at))

        return evaluated_items

    @classmethod
    def get_queue_summary_kpis(cls) -> Dict[str, int]:
        """
        Retorna as métricas e contadores consolidados da fila operacional para o Dashboard.
        """
        all_items = cls.get_queue_queryset(filters={'show_all': True})
        
        needs_review_items = [it for it in all_items if it.needs_review]
        critical_count = sum(1 for it in needs_review_items if it.priority_level == cls.PRIORITY_CRITICAL)
        high_count = sum(1 for it in needs_review_items if it.priority_level == cls.PRIORITY_HIGH)
        medium_count = sum(1 for it in needs_review_items if it.priority_level == cls.PRIORITY_MEDIUM)
        low_count = sum(1 for it in needs_review_items if it.priority_level == cls.PRIORITY_LOW)

        public_not_audited_count = sum(
            1 for it in all_items 
            if it.record.audit_status == 'not_audited' and it.record.public_display_allowed
        )

        active_takedowns_count = sum(1 for it in all_items if it.has_active_takedown)
        pending_doc_count = sum(1 for it in all_items if it.record.audit_status == 'pending')
        divergent_count = sum(1 for it in all_items if it.has_integrity_divergence)

        return {
            'total_needs_review': len(needs_review_items),
            'critical_priority_count': critical_count,
            'high_priority_count': high_count,
            'medium_priority_count': medium_count,
            'low_priority_count': low_count,
            'public_not_audited_count': public_not_audited_count,
            'active_takedowns_count': active_takedowns_count,
            'pending_documentation_count': pending_doc_count,
            'technical_divergence_count': divergent_count,
        }

    @classmethod
    def get_assisted_audit_data(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Gera os dados estruturados e limpos para a tela de Auditoria Assistida Simples (Fase 2 - Prompt 2).
        Retorna informações de procedência, status, pendência principal, ações e metadados sanitizados.
        """
        try:
            record = ImageRightsRecord.objects.select_related(
                'content_type',
                'created_by'
            ).prefetch_related(
                Prefetch('takedown_requests', queryset=CopyrightTakedownRequest.objects.all(), to_attr='prefetched_takedowns')
            ).get(pk=record_id)
        except ImageRightsRecord.DoesNotExist:
            return None

        # Avaliação centralizada da fila
        evaluated_item = cls.evaluate_record(record)

        # Pendência principal e outras pendências
        primary_reason = evaluated_item.reasons[0] if evaluated_item.reasons else "Nenhuma pendência prioritária identificada."
        other_reasons = evaluated_item.reasons[1:] if len(evaluated_item.reasons) > 1 else []

        # Imagem segura (respeitando can_display_publicly)
        image_url = ""
        has_safe_image = False
        if record.can_display_publicly and record.content_object:
            file_attr = getattr(record.content_object, record.image_field_name, None)
            if file_attr and hasattr(file_attr, 'url'):
                try:
                    image_url = file_attr.url
                    has_safe_image = True
                except Exception:
                    image_url = ""

        # Contestação ativa em análise
        active_takedown = None
        if evaluated_item.has_active_takedown:
            takedowns = getattr(record, 'prefetched_takedowns', list(record.takedown_requests.all()))
            active_list = [t for t in takedowns if t.status in ['received', 'under_review', 'awaiting_information', 'temporarily_suspended']]
            if active_list:
                active_takedown = active_list[0]

        # Verificação simples de completude operacional
        has_author = bool(record.creator_name or record.credit_name)
        has_holder = bool(record.rights_holder_name or record.license_type in ['public_domain', 'own'])
        has_origin = bool(record.provenance_provider or record.source_url or record.is_ai_generated)
        has_regime = bool(record.license_type or record.legal_basis)
        is_info_complete = has_author and has_holder and has_origin and has_regime

        # Navegação (Anterior / Próximo)
        prev_id = ImageRightsRecord.objects.filter(id__lt=record.id).order_by('-id').values_list('id', flat=True).first()
        next_id = ImageRightsRecord.objects.filter(id__gt=record.id).order_by('id').values_list('id', flat=True).first()

        # Sanitização de metadados técnicos seguros (remover credenciais, secrets, tokens)
        sanitized_metadata = {}
        if isinstance(record.provenance_metadata, dict):
            for k, v in record.provenance_metadata.items():
                k_lower = str(k).lower()
                if any(sens in k_lower for sens in ['secret', 'token', 'key', 'password', 'auth', 'cred', 'bearer', 'cookie']):
                    continue
                sanitized_metadata[k] = v

        return {
            'record': record,
            'item': evaluated_item,
            'primary_reason': primary_reason,
            'other_reasons': other_reasons,
            'image_url': image_url,
            'has_safe_image': has_safe_image,
            'active_takedown': active_takedown,
            'is_info_complete': is_info_complete,
            'prev_id': prev_id,
            'next_id': next_id,
            'sanitized_metadata': sanitized_metadata,
        }

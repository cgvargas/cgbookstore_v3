# core/services/image_rights_batch_review_service.py
"""
Serviço Central de Agrupamento Determinístico e Revisão Assistida em Lote (Fase 3B).

DIRETRIZ CENTRAL DE GOVERNANÇA:
- "Semelhança permite reaproveitar evidências. Semelhança NÃO permite presumir a mesma conclusão jurídica."
- NUNCA altera audit_status, public_display_allowed ou legal_basis em lote.
- NUNCA transforma publisher em titular da arte da capa (rights_holder_name).
- NUNCA transforma Termos de Uso institucionais em regime de licença (license_type).
- NUNCA sobrescreve registros com valores conflitantes ou exceções (contested, restricted, regularized, licença/doc específico).
- Reavaliação mandatória de elegibilidade em transação atômica para prevenção de race conditions.
- Idempotência rigorosa e geração de histórico de auditoria apenas para alterações reais.
"""

import logging
import re
from datetime import timedelta
from typing import List, Dict, Any, Optional

from django.db import transaction, models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from core.models.image_rights import ImageRightsRecord
from core.models.institutional_source import InstitutionalSource
from core.models.copyright_takedown import CopyrightTakedownRequest
from core.services.image_rights_history_service import ImageRightsHistoryService
from core.services.image_rights_research_service import ImageRightsResearchService, KNOWN_INSTITUTIONAL_SOURCES

logger = logging.getLogger(__name__)


class ImageRightsBatchReviewService:
    """
    Serviço central para agrupamento factual determinístico e aplicação assistida em lote
    de evidências institucionais e metadados de procedência.
    """

    # Matriz de classificação de campos
    PROTECTED_LEGAL_FIELDS = [
        'legal_basis',
        'audit_status',
        'public_display_allowed',
        'is_contested',
        'takedown_request',
    ]

    INDIVIDUAL_IMAGE_FIELDS = [
        'creator_name',
        'rights_holder_name',
        'licensor_name',
        'credit_name',
        'permission_document',
        'license_type',
        'usage_notes',
    ]

    TECHNICAL_PROVENANCE_FIELDS = [
        'provenance_provider',
        'provenance_method',
        'provider_asset_id',
        'is_auto_imported',
        'source_url',
    ]

    REUSABLE_INSTITUTIONAL_FIELDS = [
        'provenance_metadata',
    ]

    # Aliases determinísticos para normalização de editoras (sem fuzzy matching cego)
    PUBLISHER_CANONICAL_ALIASES = {
        'harpercollins brasil': 'HarperCollins Brasil',
        'harper collins brasil': 'HarperCollins Brasil',
        'harpercollins': 'HarperCollins Brasil',
        'harper collins': 'HarperCollins Brasil',
        'editora harpercollins': 'HarperCollins Brasil',
        'editora harpercollins brasil': 'HarperCollins Brasil',
        'companhia das letras': 'Companhia das Letras',
        'cia das letras': 'Companhia das Letras',
        'grupo companhia das letras': 'Companhia das Letras',
        'editora companhia das letras': 'Companhia das Letras',
        'record': 'Grupo Editorial Record',
        'editora record': 'Grupo Editorial Record',
        'grupo record': 'Grupo Editorial Record',
        'grupo editorial record': 'Grupo Editorial Record',
        'rocco': 'Editora Rocco',
        'editora rocco': 'Editora Rocco',
        'sextante': 'Editora Sextante',
        'editora sextante': 'Editora Sextante',
        'intrinseca': 'Editora Intrínseca',
        'intrínseca': 'Editora Intrínseca',
        'editora intrinseca': 'Editora Intrínseca',
        'editora intrínseca': 'Editora Intrínseca',
        'aleph': 'Editora Aleph',
        'editora aleph': 'Editora Aleph',
        'arqueiro': 'Editora Arqueiro',
        'editora arqueiro': 'Editora Arqueiro',
        'todavia': 'Editora Todavia',
        'editora todavia': 'Editora Todavia',
    }

    @classmethod
    def normalize_publisher_name(cls, raw_publisher: str) -> Optional[str]:
        """
        Normaliza o nome da editora utilizando correspondências determinísticas e aliases.
        Se não houver certeza, retorna o valor sanitizado ou None.
        NUNCA utiliza AI/embeddings ou fuzzy matching agressivo.
        """
        if not raw_publisher or not str(raw_publisher).strip():
            return None

        clean = re.sub(r'\s+', ' ', str(raw_publisher).strip())
        lookup_key = clean.lower()

        # 1. Aliases estáticos verificados
        if lookup_key in cls.PUBLISHER_CANONICAL_ALIASES:
            return cls.PUBLISHER_CANONICAL_ALIASES[lookup_key]

        # 2. Busca em InstitutionalSource cadastrados
        inst = InstitutionalSource.objects.filter(
            models.Q(name__iexact=clean) | models.Q(name__iexact=lookup_key)
        ).first()
        if inst:
            return inst.name

        # 3. Retorno padronizado de string limpa
        return clean

    @classmethod
    def get_institutional_evidence(cls, publisher_name: str) -> Optional[Dict[str, Any]]:
        """
        Localiza evidências institucionais de domínio e termos para uma editora normalizada.
        Reutiliza registros em banco (InstitutionalSource) ou sementes confirmadas.
        """
        if not publisher_name:
            return None

        clean_name = publisher_name.strip()
        lookup_key = clean_name.lower()

        # 1. Banco de dados
        inst = InstitutionalSource.objects.filter(
            models.Q(name__iexact=clean_name) | models.Q(name__iexact=lookup_key),
            is_active=True
        ).first()

        if inst:
            is_recent = inst.is_terms_recent
            return {
                'id': inst.id,
                'name': inst.name,
                'domain': inst.domain,
                'main_url': inst.main_url,
                'terms_url': inst.terms_url,
                'permissions_url': inst.permissions_url,
                'terms_summary': inst.terms_summary,
                'terms_content_hash': inst.terms_content_hash,
                'terms_retrieved_at': inst.terms_retrieved_at,
                'is_recent': is_recent,
                'is_verified': inst.is_verified,
                'confirmation_origin': getattr(inst, 'confirmation_origin', 'manual_admin'),
            }

        # 2. Sementes conhecidas
        if lookup_key in KNOWN_INSTITUTIONAL_SOURCES:
            seed = KNOWN_INSTITUTIONAL_SOURCES[lookup_key]
            return {
                'id': None,
                'name': clean_name,
                'domain': seed.get('domain', ''),
                'main_url': seed.get('main_url', ''),
                'terms_url': seed.get('terms_url', ''),
                'permissions_url': seed.get('permissions_url', ''),
                'terms_summary': seed.get('terms_summary', ''),
                'terms_content_hash': '',
                'terms_retrieved_at': None,
                'is_recent': False,
                'is_verified': True,
                'confirmation_origin': 'verified_seed',
            }

        return None

    @classmethod
    def get_review_groups(cls) -> List[Dict[str, Any]]:
        """
        Identifica e monta a lista determinística de grupos de revisão assistida.
        Executa agregações eficientes no banco sem N+1 e sem chamadas de rede externas.
        """
        groups = []

        # ContentType de Livro
        book_ct = ContentType.objects.filter(app_label='core', model='book').first()

        # -------------------------------------------------------------
        # 1. Agrupamento por Editora Confirmada (Model Book)
        # -------------------------------------------------------------
        if book_ct:
            from core.models.book import Book

            # Buscar editoras distintas de livros com ImageRightsRecord
            book_records = ImageRightsRecord.objects.filter(
                content_type=book_ct,
                image_field_name='cover_image'
            ).values_list('object_id', flat=True)

            publishers = Book.objects.filter(
                id__in=book_records
            ).exclude(
                publisher=''
            ).values_list('publisher', flat=True).distinct()

            # Mapear editoras normalizadas
            norm_publishers_map = {}
            for raw_pub in publishers:
                norm_pub = cls.normalize_publisher_name(raw_pub)
                if norm_pub:
                    if norm_pub not in norm_publishers_map:
                        norm_publishers_map[norm_pub] = []
                    norm_publishers_map[norm_pub].append(raw_pub)

            for norm_pub, raw_list in norm_publishers_map.items():
                book_ids = list(Book.objects.filter(publisher__in=raw_list).values_list('id', flat=True))
                records_qs = ImageRightsRecord.objects.filter(
                    content_type=book_ct,
                    object_id__in=book_ids,
                    image_field_name='cover_image'
                )

                total_count = records_qs.count()
                if total_count == 0:
                    continue

                # Evidência institucional
                inst_evidence = cls.get_institutional_evidence(norm_pub)

                # Calcular exceções e pendências
                pending_count = records_qs.filter(
                    audit_status__in=['not_audited', 'under_review', 'pending']
                ).count()

                # Análise rápida de exceções
                exceptions_count = cls._count_exceptions_in_queryset(records_qs, inst_evidence)
                eligible_count = max(0, total_count - exceptions_count)

                # Chave única explicável
                slug_key = re.sub(r'[^a-zA-Z0-9_]+', '_', norm_pub.lower()).strip('_')
                group_key = f"pub_{slug_key}"

                groups.append({
                    'group_key': group_key,
                    'group_type': 'publisher',
                    'canonical_name': norm_pub,
                    'title': f"{norm_pub} — Capas de Livros",
                    'explanation': f"Mesma editora ({norm_pub}), mesmo tipo de imagem (capas de livros) e evidências institucionais compartilháveis.",
                    'total_records': total_count,
                    'pending_records_count': pending_count,
                    'exceptions_count': exceptions_count,
                    'eligible_count': eligible_count,
                    'institutional_evidence': inst_evidence,
                    'has_terms': bool(inst_evidence and inst_evidence.get('terms_url')),
                    'terms_url': inst_evidence.get('terms_url') if inst_evidence else '',
                    'official_domain': inst_evidence.get('domain') if inst_evidence else '',
                    'is_terms_recent': inst_evidence.get('is_recent', False) if inst_evidence else False,
                })

        # -------------------------------------------------------------
        # 2. Agrupamento por Provedor Técnico de Procedência
        # -------------------------------------------------------------
        providers = ImageRightsRecord.objects.exclude(
            provenance_provider=''
        ).values('provenance_provider', 'image_field_name').annotate(
            total_count=models.Count('id')
        ).order_by('-total_count')

        for prov_item in providers:
            provider_code = prov_item['provenance_provider']
            field_name = prov_item['image_field_name']

            prov_display = dict(ImageRightsRecord.PROVENANCE_PROVIDER_CHOICES).get(provider_code, provider_code)
            
            records_qs = ImageRightsRecord.objects.filter(
                provenance_provider=provider_code,
                image_field_name=field_name
            )

            total_count = prov_item['total_count']
            if total_count == 0:
                continue

            pending_count = records_qs.filter(
                audit_status__in=['not_audited', 'under_review', 'pending']
            ).count()

            exceptions_count = cls._count_exceptions_in_queryset(records_qs, None)
            eligible_count = max(0, total_count - exceptions_count)

            group_key = f"prov_{provider_code}_{field_name}"

            groups.append({
                'group_key': group_key,
                'group_type': 'provenance_provider',
                'canonical_name': prov_display,
                'title': f"{prov_display} — Ativos ({field_name})",
                'explanation': f"Mesmo provedor técnico ({prov_display}) e mesmo campo de imagem ({field_name}).",
                'total_records': total_count,
                'pending_records_count': pending_count,
                'exceptions_count': exceptions_count,
                'eligible_count': eligible_count,
                'institutional_evidence': None,
                'has_terms': False,
                'terms_url': '',
                'official_domain': '',
                'is_terms_recent': False,
            })

        # Ordenar por pendências e total
        groups.sort(key=lambda g: (g['pending_records_count'], g['total_records']), reverse=True)
        return groups

    @classmethod
    def is_source_url_divergent(cls, rec: ImageRightsRecord, inst_evidence: Optional[Dict[str, Any]]) -> bool:
        """
        Verifica se a source_url do registro aponta para uma fonte desconhecida/conflitante
        que não seja o próprio provedor técnico da imagem ou o domínio oficial da editora.
        """
        if not rec.source_url:
            return False
        url_lower = rec.source_url.lower()

        # Provedor técnico Google Books
        if rec.provenance_provider == 'google_books' and ('google.' in url_lower or 'googleusercontent.com' in url_lower):
            return False

        # Provedor técnico Amazon
        if rec.provenance_provider == 'amazon' and ('amazon.' in url_lower or 'ssl-images-amazon' in url_lower or 'media-amazon' in url_lower):
            return False

        # Provedor técnico Open Library
        if rec.provenance_provider == 'open_library' and ('openlibrary.org' in url_lower or 'archive.org' in url_lower):
            return False

        # Domínio oficial da editora
        if inst_evidence and inst_evidence.get('domain'):
            if inst_evidence['domain'].lower() in url_lower:
                return False

        # Caso contrário, fonte externa desconhecida/divergente
        return True

    @classmethod
    def _count_exceptions_in_queryset(cls, queryset, institutional_evidence: Optional[Dict[str, Any]]) -> int:
        """
        Calcula a quantidade de registros que contêm exceções que os tornam
        inelegíveis para aplicação automática por padrão.
        """
        active_takedown_records = set(
            CopyrightTakedownRequest.objects.filter(
                status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
            ).values_list('image_rights_record_id', flat=True)
        )

        count = 0
        for rec in queryset:
            if rec.audit_status in ['contested', 'restricted', 'regularized']:
                count += 1
            elif rec.id in active_takedown_records:
                count += 1
            elif rec.permission_document:
                count += 1
            elif rec.license_type and rec.license_type not in ['', 'publisher', 'google_books', 'open_library', 'amazon']:
                count += 1
            elif rec.creator_name or rec.rights_holder_name:
                count += 1
            elif cls.is_source_url_divergent(rec, institutional_evidence):
                count += 1
        return count

    @classmethod
    def get_group_detail(cls, group_key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera os detalhes completos de um grupo determinístico, incluindo todos os seus registros,
        avaliação de elegibilidade e exceções por item.
        """
        if not group_key:
            return None

        all_groups = cls.get_review_groups()
        group_info = next((g for g in all_groups if g['group_key'] == group_key), None)
        if not group_info:
            return None

        # Identificar o tipo de grupo
        if group_key.startswith('pub_'):
            norm_pub = group_info['canonical_name']
            book_ct = ContentType.objects.filter(app_label='core', model='book').first()
            if not book_ct:
                return None

            from core.models.book import Book
            raw_publishers = [
                raw for raw, canon in cls.PUBLISHER_CANONICAL_ALIASES.items()
                if canon.lower() == norm_pub.lower()
            ]
            raw_publishers.append(norm_pub)

            book_ids = list(Book.objects.filter(
                models.Q(publisher__in=raw_publishers) | models.Q(publisher__iexact=norm_pub)
            ).values_list('id', flat=True))

            records = list(ImageRightsRecord.objects.filter(
                content_type=book_ct,
                object_id__in=book_ids,
                image_field_name='cover_image'
            ).select_related('content_type').order_by('id'))

            inst_evidence = group_info['institutional_evidence']

        elif group_key.startswith('prov_'):
            parts = group_key[5:].split('_')
            if len(parts) < 2:
                return None
            provider_code = parts[0]
            field_name = "_".join(parts[1:])

            records = list(ImageRightsRecord.objects.filter(
                provenance_provider=provider_code,
                image_field_name=field_name
            ).select_related('content_type').order_by('id'))

            inst_evidence = None
        else:
            return None

        active_takedown_record_ids = set(
            CopyrightTakedownRequest.objects.filter(
                status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
            ).values_list('image_rights_record_id', flat=True)
        )

        analyzed_records = []
        eligible_count = 0
        exceptions_count = 0

        for rec in records:
            exceptions = []
            is_eligible = True

            # 1. Contestação ativa
            if rec.audit_status == 'contested' or rec.id in active_takedown_record_ids:
                exceptions.append("⚠ Contestação formal ativa ou takedown em andamento")
                is_eligible = False

            # 2. Restrito
            if rec.audit_status == 'restricted':
                exceptions.append("⚠ Registro com uso restrito / suspenso administrativamente")
                is_eligible = False

            # 3. Regularizado
            if rec.audit_status == 'regularized':
                exceptions.append("⚠ Registro já regularizado (protegido contra alteração em lote)")
                is_eligible = False

            # 4. Licença específica pré-existente
            if rec.license_type and rec.license_type not in ['', 'publisher', 'google_books', 'open_library', 'amazon']:
                exceptions.append(f"⚠ Licença específica existente ({rec.get_license_type_display()})")
                is_eligible = False

            # 5. Documento comprobatório anexado
            if rec.permission_document:
                exceptions.append("⚠ Documento comprobatório privado anexado")
                is_eligible = False

            # 6. Criador ou titular específico já registrado
            if rec.creator_name:
                exceptions.append(f"⚠ Criador específico informado ({rec.creator_name})")
                is_eligible = False
            if rec.rights_holder_name:
                exceptions.append(f"⚠ Titular específico informado ({rec.rights_holder_name})")
                is_eligible = False

            # 7. Divergência técnica ou conflito de URL
            if cls.is_source_url_divergent(rec, inst_evidence):
                exceptions.append(f"⚠ Fonte existente aponta para domínio diferente ({rec.source_url[:40]}...)")
                is_eligible = False

            if is_eligible:
                eligible_count += 1
            else:
                exceptions_count += 1

            image_url = None
            has_safe_image = False
            try:
                if rec.content_object and hasattr(rec.content_object, rec.image_field_name):
                    img_file = getattr(rec.content_object, rec.image_field_name)
                    if img_file and hasattr(img_file, 'url'):
                        image_url = img_file.url
                        has_safe_image = rec.can_display_publicly
            except Exception:
                pass

            analyzed_records.append({
                'record': rec,
                'id': rec.id,
                'work_title': rec.work_title or (str(rec.content_object) if rec.content_object else f"Registro #{rec.id}"),
                'audit_status': rec.audit_status,
                'audit_status_display': rec.get_audit_status_display(),
                'provenance_provider': rec.provenance_provider,
                'provenance_provider_display': rec.get_provenance_provider_display(),
                'source_url': rec.source_url,
                'license_type': rec.license_type,
                'creator_name': rec.creator_name,
                'rights_holder_name': rec.rights_holder_name,
                'is_eligible': is_eligible,
                'exceptions': exceptions,
                'has_safe_image': has_safe_image,
                'image_url': image_url,
            })

        return {
            'group_key': group_key,
            'group_info': group_info,
            'institutional_evidence': inst_evidence,
            'records': analyzed_records,
            'total_records': len(analyzed_records),
            'eligible_count': eligible_count,
            'exceptions_count': exceptions_count,
        }

    @classmethod
    def preview_batch_update(
        cls,
        group_key: str,
        selected_record_ids: List[int],
        fields_to_apply: List[str]
    ) -> Dict[str, Any]:
        """
        Calcula e simula com precisão as alterações que seriam aplicadas aos registros selecionados,
        sem persistir nada no banco de dados e sem gerar logs de histórico.
        """
        detail = cls.get_group_detail(group_key)
        if not detail:
            return {'success': False, 'message': 'Grupo de revisão não encontrado.'}

        inst_evidence = detail.get('institutional_evidence')
        records_map = {r['id']: r for r in detail['records']}

        safe_fields = [
            f for f in fields_to_apply
            if f in cls.REUSABLE_INSTITUTIONAL_FIELDS and f not in cls.PROTECTED_LEGAL_FIELDS
        ]

        proposed_updates = []
        ignored_records = []
        no_change_records = []

        for rec_id in selected_record_ids:
            item = records_map.get(rec_id)
            if not item:
                continue

            rec = item['record']

            if not item['is_eligible']:
                ignored_records.append({
                    'id': rec.id,
                    'work_title': item['work_title'],
                    'reasons': item['exceptions']
                })
                continue

            changes = {}
            if 'provenance_metadata' in safe_fields and inst_evidence:
                current_meta = dict(rec.provenance_metadata or {})
                new_inst_meta = {
                    'institutional_source': inst_evidence.get('name'),
                    'official_domain': inst_evidence.get('domain'),
                    'institutional_main_url': inst_evidence.get('main_url', ''),
                    'institutional_terms_url': inst_evidence.get('terms_url', ''),
                    'institutional_rights_url': inst_evidence.get('permissions_url', ''),
                    'institutional_terms_summary': inst_evidence.get('terms_summary', ''),
                    'institutional_terms_hash': inst_evidence.get('terms_content_hash', ''),
                }
                if inst_evidence.get('terms_retrieved_at'):
                    new_inst_meta['institutional_terms_retrieved_at'] = inst_evidence['terms_retrieved_at'].isoformat()

                diff_detected = False
                for k, v in new_inst_meta.items():
                    if current_meta.get(k) != v:
                        diff_detected = True
                        break

                if diff_detected:
                    changes['provenance_metadata'] = {
                        'field_label': 'Evidência Institucional Complementar',
                        'old_value': current_meta.get('institutional_source') or '(Sem vínculo institucional)',
                        'new_value': f"{inst_evidence.get('name')} ({inst_evidence.get('domain')})",
                    }

            if changes:
                proposed_updates.append({
                    'id': rec.id,
                    'work_title': item['work_title'],
                    'changes': changes
                })
            else:
                no_change_records.append({
                    'id': rec.id,
                    'work_title': item['work_title'],
                    'reason': 'Os valores já estão atualizados com as informações institucionais.'
                })

        return {
            'success': True,
            'group_key': group_key,
            'safe_fields': safe_fields,
            'total_selected': len(selected_record_ids),
            'eligible_for_update_count': len(proposed_updates),
            'ignored_count': len(ignored_records),
            'no_change_count': len(no_change_records),
            'proposed_updates': proposed_updates,
            'ignored_records': ignored_records,
            'no_change_records': no_change_records,
        }

    @classmethod
    def apply_batch_update(
        cls,
        group_key: str,
        selected_record_ids: List[int],
        fields_to_apply: List[str],
        performed_by=None
    ) -> Dict[str, Any]:
        """
        Executa a aplicação atômica e segura das informações factuais nos registros confirmados.
        Recalcula a elegibilidade dentro de transaction.atomic() para proteção contra race conditions.
        NUNCA altera legal_basis, audit_status, public_display_allowed, provenance_provider ou source_url.
        """
        if not selected_record_ids or not fields_to_apply:
            return {
                'success': False,
                'message': 'Nenhum registro ou campo selecionado para aplicação.',
                'updated_count': 0,
                'ignored_count': 0,
                'failed_count': 0,
            }

        safe_fields = [
            f for f in fields_to_apply
            if f in cls.REUSABLE_INSTITUTIONAL_FIELDS and f not in cls.PROTECTED_LEGAL_FIELDS
        ]

        if not safe_fields:
            return {
                'success': False,
                'message': 'Nenhum campo seguro selecionado para aplicação.',
                'updated_count': 0,
                'ignored_count': 0,
                'failed_count': 0,
            }

        detail = cls.get_group_detail(group_key)
        if not detail:
            return {
                'success': False,
                'message': 'Grupo de revisão não localizado.',
                'updated_count': 0,
                'ignored_count': 0,
                'failed_count': 0,
            }

        inst_evidence = detail.get('institutional_evidence')

        updated_records = []
        ignored_records = []
        failed_records = []

        with transaction.atomic():
            records_qs = ImageRightsRecord.objects.select_for_update().filter(id__in=selected_record_ids)
            records_by_id = {r.id: r for r in records_qs}

            active_takedowns = set(
                CopyrightTakedownRequest.objects.filter(
                    status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
                ).values_list('image_rights_record_id', flat=True)
            )

            for rec_id in selected_record_ids:
                rec = records_by_id.get(rec_id)
                if not rec:
                    ignored_records.append({'id': rec_id, 'reason': 'Registro não encontrado no banco.'})
                    continue

                if rec.audit_status in ['contested', 'restricted', 'regularized']:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': f'Status protegido ({rec.get_audit_status_display()}) — ignorado por segurança.'
                    })
                    continue

                if rec.id in active_takedowns:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Contestação formal recebida recentemente — ignorado por segurança.'
                    })
                    continue

                if rec.permission_document:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Documento comprobatório privado anexado — protegido.'
                    })
                    continue

                if rec.license_type and rec.license_type not in ['', 'publisher', 'google_books', 'open_library', 'amazon']:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Licença específica existente — protegido.'
                    })
                    continue

                if rec.creator_name or rec.rights_holder_name:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Criador ou titular individual existente — protegido.'
                    })
                    continue

                if cls.is_source_url_divergent(rec, inst_evidence):
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Fonte existente aponta para domínio divergente — protegido.'
                    })
                    continue

                has_changes = False

                if 'provenance_metadata' in safe_fields and inst_evidence:
                    current_meta = dict(rec.provenance_metadata or {})
                    new_inst_meta = {
                        'institutional_source': inst_evidence.get('name'),
                        'official_domain': inst_evidence.get('domain'),
                        'institutional_main_url': inst_evidence.get('main_url', ''),
                        'institutional_terms_url': inst_evidence.get('terms_url', ''),
                        'institutional_rights_url': inst_evidence.get('permissions_url', ''),
                        'institutional_terms_summary': inst_evidence.get('terms_summary', ''),
                        'institutional_terms_hash': inst_evidence.get('terms_content_hash', ''),
                    }
                    if inst_evidence.get('terms_retrieved_at'):
                        new_inst_meta['institutional_terms_retrieved_at'] = inst_evidence['terms_retrieved_at'].isoformat()

                    diff_detected = False
                    for k, v in new_inst_meta.items():
                        if current_meta.get(k) != v:
                            current_meta[k] = v
                            diff_detected = True

                    if diff_detected:
                        rec.provenance_metadata = current_meta
                        has_changes = True

                if has_changes:
                    rec.save(update_fields=['provenance_metadata', 'updated_at'])

                    ImageRightsHistoryService.log_event(
                        image_rights_record=rec,
                        event_type='record_updated',
                        description="Informação factual aplicada após confirmação em revisão assistida em lote.",
                        performed_by=performed_by,
                        source='batch_review',
                        field_name="provenance_metadata",
                        metadata={
                            'batch_group': group_key,
                            'fields_applied': ['provenance_metadata'],
                            'institutional_source': inst_evidence.get('name') if inst_evidence else None,
                        }
                    )
                    updated_records.append(rec.id)
                else:
                    ignored_records.append({
                        'id': rec.id,
                        'reason': 'Nenhuma alteração necessária (valores já sincronizados).'
                    })

        logger.info(
            f"[ImageRightsBatchReviewService] Lote '{group_key}' aplicado: "
            f"{len(updated_records)} atualizados, {len(ignored_records)} ignorados."
        )

        return {
            'success': True,
            'group_key': group_key,
            'updated_count': len(updated_records),
            'ignored_count': len(ignored_records),
            'failed_count': len(failed_records),
            'updated_records': updated_records,
            'ignored_records': ignored_records,
        }

    @classmethod
    def research_group_records(cls, group_key: str, performed_by=None) -> Dict[str, Any]:
        """
        Executa a pesquisa factual para o grupo de forma inteligente:
        1. Consulta a fonte institucional e os termos uma única vez para o grupo.
        2. Realiza pesquisas direcionadas por ISBN apenas para registros que não possuam metadados.
        Evita chamadas redundantes para a mesma instituição.
        """
        detail = cls.get_group_detail(group_key)
        if not detail:
            return {'success': False, 'message': 'Grupo não encontrado.'}

        group_info = detail.get('group_info')
        norm_pub = group_info.get('canonical_name') if group_info else None

        if norm_pub:
            inst = InstitutionalSource.objects.filter(name__iexact=norm_pub, is_active=True).first()
            if not inst or not inst.is_terms_recent:
                try:
                    seed = KNOWN_INSTITUTIONAL_SOURCES.get(norm_pub.lower(), {})
                    domain = seed.get('domain') or (inst.domain if inst else '')
                    if domain:
                        inst_obj, _ = InstitutionalSource.objects.get_or_create(
                            domain=domain,
                            defaults={
                                'name': norm_pub,
                                'main_url': seed.get('main_url', f"https://{domain}"),
                                'terms_url': seed.get('terms_url', ''),
                                'institution_type': seed.get('institution_type', 'publisher'),
                                'terms_summary': seed.get('terms_summary', ''),
                                'is_verified': True,
                            }
                        )
                        inst_obj.terms_retrieved_at = timezone.now()
                        inst_obj.save()
                except Exception as e:
                    logger.warning(f"Erro ao atualizar fonte institucional do grupo: {e}")

        researched_count = 0
        for item in detail['records']:
            rec = item['record']
            if not rec.source_url or not rec.work_title:
                try:
                    ImageRightsResearchService.get_or_create_research(rec.id, performed_by=performed_by)
                    researched_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao pesquisar registro #{rec.id} no grupo: {e}")

        return {
            'success': True,
            'message': f"Pesquisa concluída. Fonte institucional verificada e {researched_count} registros complementados.",
            'researched_count': researched_count,
        }

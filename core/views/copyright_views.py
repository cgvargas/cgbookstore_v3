# core/views/copyright_views.py
"""
Views para a Dashboard Administrativa de Auditoria de Direitos Autorais de Imagens,
Mapa de Conformidade de Ativos Visuais por Modelo
e para o Acesso Seguro/Protegido aos Documentos de Autorização.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import render, get_object_or_404
from django.db import models
from core.models.image_rights import ImageRightsRecord
from core.models.copyright_takedown import CopyrightTakedownRequest
from core.services.image_rights_service import ImageRightsAuditService


@staff_member_required
def copyright_audit_dashboard(request):
    """
    Dashboard Corporativa de Auditoria de Direitos Autorais e Governança de Ativos Visuais.
    Calcula:
    1. Taxa de Atribuição e Procedência (%)
    2. Taxa de Comprovação Jurídica (%)
    3. Fila de Pendências e Tabela de Registros com links diretos para correção.
    4. Painel de Contestações, Notificações e Procedimentos de Takedown.
    """
    total_records = ImageRightsRecord.objects.count()

    # 1. Filtros e Indicadores de Estado de Auditoria
    not_audited_count = ImageRightsRecord.objects.filter(audit_status='not_audited').count()
    under_review_count = ImageRightsRecord.objects.filter(audit_status='under_review').count()
    regularized_count = ImageRightsRecord.objects.filter(audit_status='regularized').count()
    pending_audit_count = ImageRightsRecord.objects.filter(audit_status='pending').count()
    contested_count = ImageRightsRecord.objects.filter(audit_status='contested').count()
    restricted_count = ImageRightsRecord.objects.filter(audit_status='restricted').count()

    # 2. Métricas e Painel de Contestações e Notificações (Takedowns)
    total_takedowns = CopyrightTakedownRequest.objects.count()
    open_takedowns_count = CopyrightTakedownRequest.objects.filter(
        status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
    ).count()
    takedown_under_review_count = CopyrightTakedownRequest.objects.filter(status='under_review').count()
    takedown_awaiting_info_count = CopyrightTakedownRequest.objects.filter(status='awaiting_information').count()
    takedown_suspended_count = CopyrightTakedownRequest.objects.filter(status='temporarily_suspended').count()
    takedown_resolved_keep_count = CopyrightTakedownRequest.objects.filter(status='resolved_keep').count()
    takedown_resolved_removed_count = CopyrightTakedownRequest.objects.filter(status='resolved_removed').count()
    takedown_rejected_count = CopyrightTakedownRequest.objects.filter(status='rejected').count()

    active_takedowns = CopyrightTakedownRequest.objects.filter(
        status__in=['received', 'under_review', 'awaiting_information', 'temporarily_suspended']
    ).select_related('image_rights_record', 'image_rights_record__content_type').order_by('-received_at')[:15]

    # Distribuição por Estado de Auditoria
    audit_status_distribution = []
    for code, label in ImageRightsRecord.AUDIT_STATUS_CHOICES:
        count = ImageRightsRecord.objects.filter(audit_status=code).count()
        if count > 0:
            audit_status_distribution.append({'code': code, 'label': label, 'count': count})

    records_with_license = ImageRightsRecord.objects.exclude(license_type='')
    unlicensed_records = ImageRightsRecord.objects.filter(license_type='')
    ai_generated_records = ImageRightsRecord.objects.filter(is_ai_generated=True)
    records_with_doc = ImageRightsRecord.objects.exclude(permission_document='')

    # Distribuição por Licença / Procedência
    license_distribution = []
    for code, label in ImageRightsRecord.LICENSE_CHOICES:
        count = ImageRightsRecord.objects.filter(license_type=code).count()
        if count > 0:
            license_distribution.append({'code': code, 'label': label, 'count': count})
    
    # Adicionar sem licença
    if unlicensed_records.exists():
        license_distribution.append({'code': '', 'label': '⚠️ Sem Licença Informada', 'count': unlicensed_records.count()})

    # Distribuição por Finalidade do Uso
    purpose_distribution = []
    for code, label in ImageRightsRecord.PURPOSE_CHOICES:
        count = ImageRightsRecord.objects.filter(usage_purpose=code).count()
        if count > 0:
            purpose_distribution.append({'code': code, 'label': label, 'count': count})

    # Distribuição por Fundamento Jurídico
    legal_basis_distribution = []
    for code, label in ImageRightsRecord.LEGAL_BASIS_CHOICES:
        count = ImageRightsRecord.objects.filter(legal_basis=code).count()
        if count > 0:
            legal_basis_distribution.append({'code': code, 'label': label, 'count': count})

    # Registros com Especificações de Dimensão / Resolução Auditadas
    records_with_specs_count = ImageRightsRecord.objects.exclude(display_dimensions='').count()

    # 3. Cálculo da Taxa de Atribuição e Procedência (%) e Comprovação Jurídica
    valid_attribution_count = 0
    valid_legal_proof_count = 0

    all_records = list(ImageRightsRecord.objects.select_related('content_type').all())
    pending_records = []

    for rec in all_records:
        has_attribution = False
        has_legal_proof = False
        issues = []

        # Regra de Atribuição e Procedência (TASL)
        author_identifier = rec.creator_name or rec.credit_name
        if rec.license_type or rec.legal_basis:
            if rec.license_type == 'cc':
                if author_identifier and rec.source_url and rec.license_url:
                    has_attribution = True
                else:
                    if not rec.license_url:
                        issues.append("CC sem URL oficial da Licença")
                    if not rec.source_url:
                        issues.append("CC sem URL da Fonte original")
                    if not author_identifier:
                        issues.append("CC sem indicação de criador/autor")
            elif rec.license_type == 'own' or rec.legal_basis == 'own_production':
                has_attribution = True
            elif rec.license_type == 'licensed' or rec.legal_basis == 'express_consent':
                if author_identifier or rec.rights_holder_name or rec.licensor_name:
                    has_attribution = True
                else:
                    issues.append("Licença/Autorização sem titular, licenciante ou criador identificado")
            elif rec.license_type == 'public_domain' or rec.legal_basis == 'public_domain':
                if author_identifier or rec.source_url:
                    has_attribution = True
                else:
                    issues.append("Domínio Público sem autor ou fonte")
            elif rec.legal_basis == 'fair_use_art46':
                if author_identifier or rec.source_url:
                    has_attribution = True
                else:
                    issues.append("Limitação legal (Art. 46) sem indicação de criador/autor ou fonte")
            elif rec.license_type in ['publisher', 'amazon', 'google_books', 'open_library', 'wikimedia']:
                if author_identifier or rec.source_url:
                    has_attribution = True
                else:
                    issues.append("Origem de catálogo/plataforma sem criador ou fonte")
            elif author_identifier or rec.source_url:
                has_attribution = True

        if has_attribution:
            valid_attribution_count += 1

        # Regra de Comprovação Jurídica / Governança
        if rec.audit_status == 'contested':
            has_legal_proof = False
            issues.append("Ativo formalmente contestado ou sob disputa de direitos autorais")
        elif rec.audit_status == 'restricted':
            has_legal_proof = False
            issues.append("Uso suspenso ou restrito administrativamente")
        elif rec.audit_status == 'not_audited':
            has_legal_proof = False
            issues.append("Registro cadastrado mas ainda não auditado administrativamente")
        elif rec.audit_status == 'under_review':
            has_legal_proof = False
            issues.append("Registro em análise documental/jurídica")
        elif rec.audit_status == 'pending':
            has_legal_proof = False
            issues.append("Pendente de documentação de suporte")
        elif rec.audit_status == 'regularized':
            # Avaliar conformidade documental do registro regularizado
            if rec.license_type == 'own' or rec.legal_basis == 'own_production':
                has_legal_proof = True
            elif rec.legal_basis == 'express_consent':
                if rec.permission_document or rec.usage_notes:
                    has_legal_proof = True
                else:
                    issues.append("Autorização expressa sem documento ou observação interna comprobatória")
            elif rec.license_type == 'licensed':
                if rec.permission_document or rec.usage_notes:
                    has_legal_proof = True
                else:
                    issues.append("Licença comercial sem documento comprobatório ou observação interna")
            elif rec.license_type == 'cc' or rec.legal_basis == 'creative_commons':
                if rec.license_url and rec.source_url:
                    has_legal_proof = True
                else:
                    issues.append("Creative Commons com pendência de URL da licença ou fonte")
            elif rec.license_type == 'public_domain' or rec.legal_basis == 'public_domain':
                if rec.source_url or rec.usage_notes:
                    has_legal_proof = True
                else:
                    issues.append("Domínio público sem indicação de fonte ou fundamentação")
            elif rec.legal_basis == 'amazon_affiliate_terms':
                has_legal_proof = True
            elif rec.legal_basis == 'fair_use_art46':
                # Limitação legal analisada (Art. 46): justificativa jurídica registrada pelo administrador
                if not rec.usage_purpose:
                    issues.append("Limitação legal (Art. 46) sem finalidade de uso especificada")
                if not author_identifier and not rec.source_url:
                    issues.append("Limitação legal (Art. 46) sem indicação de criador/autor ou origem")
                if rec.usage_purpose and (author_identifier or rec.source_url):
                    has_legal_proof = True
            elif rec.license_type in ['publisher', 'amazon', 'google_books', 'open_library', 'wikimedia']:
                issues.append("Procedência de catálogo/plataforma registrada sem documento de licença ou fundamento jurídico complementar")

        if has_legal_proof:
            valid_legal_proof_count += 1

        # Adicionar à fila de pendências
        if issues or (not rec.license_type and not rec.legal_basis) or rec.audit_status in ['contested', 'restricted', 'not_audited', 'pending', 'under_review']:
            obj_name = f"ID #{rec.object_id}"
            if rec.content_object:
                obj_name = str(rec.content_object)
            
            pending_records.append({
                'record': rec,
                'obj_name': obj_name,
                'issues': issues
            })

    attribution_rate = round((valid_attribution_count / total_records * 100), 1) if total_records > 0 else 100.0
    legal_proof_rate = round((valid_legal_proof_count / total_records * 100), 1) if total_records > 0 else 100.0

    context = {
        'total_records': total_records,
        'not_audited_count': not_audited_count,
        'under_review_count': under_review_count,
        'regularized_count': regularized_count,
        'pending_audit_count': pending_audit_count,
        'contested_count': contested_count,
        'restricted_count': restricted_count,
        'unlicensed_count': unlicensed_records.count(),
        'ai_generated_count': ai_generated_records.count(),
        'with_doc_count': records_with_doc.count(),
        'records_with_specs_count': records_with_specs_count,
        'attribution_rate': attribution_rate,
        'legal_proof_rate': legal_proof_rate,
        'audit_status_distribution': audit_status_distribution,
        'license_distribution': license_distribution,
        'purpose_distribution': purpose_distribution,
        'legal_basis_distribution': legal_basis_distribution,
        'pending_records': pending_records[:100],
        'pending_total': len(pending_records),
        # Dados de Contestações / Takedown
        'total_takedowns': total_takedowns,
        'open_takedowns_count': open_takedowns_count,
        'takedown_under_review_count': takedown_under_review_count,
        'takedown_awaiting_info_count': takedown_awaiting_info_count,
        'takedown_suspended_count': takedown_suspended_count,
        'takedown_resolved_keep_count': takedown_resolved_keep_count,
        'takedown_resolved_removed_count': takedown_resolved_removed_count,
        'takedown_rejected_count': takedown_rejected_count,
        'active_takedowns': active_takedowns,
    }

    return render(request, 'admin/copyright_audit.html', context)


@staff_member_required
def copyright_compliance_map(request):
    """
    Página do Mapa de Conformidade de Ativos Visuais.
    Calcula o percentual de conformidade de cada modelo da aplicação.
    Usa ImageRightsAuditService.get_auditable_models() como fonte centralizada.
    """
    models_to_audit = ImageRightsAuditService.get_auditable_models()
    compliance_map = []

    for m in models_to_audit:
        stats = ImageRightsAuditService.get_model_compliance_stats(m)
        compliance_map.append(stats)

    context = {
        'compliance_map': compliance_map,
    }
    return render(request, 'admin/copyright_compliance_map.html', context)


@staff_member_required
def protected_copyright_document_download(request, record_id):
    """
    View de Acesso Privado aos Documentos de Autorização/Contratos.
    Requer autenticação de staff. Não expõe o arquivo publicamente.
    """
    record = get_object_or_404(ImageRightsRecord, pk=record_id)

    if not record.permission_document:
        raise Http404("Documento de autorização não cadastrado para este registro.")

    file_handle = record.permission_document
    try:
        response = FileResponse(file_handle.open('rb'))
        response['Content-Disposition'] = f'inline; filename="{file_handle.name.split("/")[-1]}"'
        return response
    except Exception as e:
        raise Http404(f"Erro ao abrir arquivo de autorização: {e}")


@staff_member_required
def protected_takedown_document_download(request, takedown_id):
    """
    View de Acesso Privado aos Documentos Probatórios de Contestações e Notificações de Takedown.
    Requer autenticação de staff. Não expõe o arquivo publicamente.
    """
    takedown = get_object_or_404(CopyrightTakedownRequest, pk=takedown_id)

    if not takedown.evidence_document:
        raise Http404("Documento comprobatório não cadastrado para esta ocorrência.")

    file_handle = takedown.evidence_document
    try:
        response = FileResponse(file_handle.open('rb'))
        response['Content-Disposition'] = f'inline; filename="{file_handle.name.split("/")[-1]}"'
        return response
    except Exception as e:
        raise Http404(f"Erro ao abrir documento comprobatório de contestação: {e}")

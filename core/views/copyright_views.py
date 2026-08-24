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
from core.models import Book, Author, LiteraryUniverse, Banner, Section, Event
from news.models import Article, Quiz
from core.services.image_rights_service import ImageRightsAuditService


@staff_member_required
def copyright_audit_dashboard(request):
    """
    Dashboard Corporativa de Auditoria de Direitos Autorais e Governança de Ativos Visuais.
    Calcula:
    1. Taxa de Atribuição e Procedência (%)
    2. Taxa de Comprovação Jurídica (%)
    3. Fila de Pendências e Tabela de Registros com links diretos para correção.
    """
    total_records = ImageRightsRecord.objects.count()

    # 1. Filtros e Indicadores
    records_with_license = ImageRightsRecord.objects.exclude(license_type='')
    unlicensed_records = ImageRightsRecord.objects.filter(license_type='')
    ai_generated_records = ImageRightsRecord.objects.filter(is_ai_generated=True)
    records_with_doc = ImageRightsRecord.objects.exclude(permission_document='')

    # Distribuição por Licença
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

    # 2. Cálculo da Taxa de Atribuição e Procedência (%)
    valid_attribution_count = 0
    valid_legal_proof_count = 0

    all_records = list(ImageRightsRecord.objects.select_related('content_type').all())
    pending_records = []

    for rec in all_records:
        has_attribution = False
        has_legal_proof = False
        issues = []

        # Regra de Atribuição
        if rec.license_type or rec.legal_basis:
            if rec.license_type == 'cc':
                if rec.credit_name and rec.source_url and rec.license_url:
                    has_attribution = True
                else:
                    if not rec.license_url:
                        issues.append("CC sem URL da Licença")
                    if not rec.source_url:
                        issues.append("CC sem URL da Fonte")
            elif rec.credit_name or rec.source_url or rec.license_type in ['own', 'publisher', 'amazon', 'google_books'] or rec.legal_basis:
                has_attribution = True
        else:
            issues.append("Licença/Fundamento não informado")

        if has_attribution:
            valid_attribution_count += 1

        # Regra de Comprovação Jurídica
        if rec.legal_basis == 'fair_use_art46' or rec.license_type == 'own' or rec.legal_basis == 'own_production':
            has_legal_proof = True
        elif rec.license_type in ['licensed', 'other']:
            if rec.permission_document or rec.usage_notes:
                has_legal_proof = True
            else:
                issues.append("Licenciada sem Documento ou Observação Interna")
        elif rec.license_type in ['publisher', 'amazon', 'google_books', 'open_library', 'wikimedia'] or rec.legal_basis == 'amazon_affiliate_terms':
            has_legal_proof = True
        elif rec.license_type in ['cc', 'public_domain']:
            if rec.source_url or rec.license_url:
                has_legal_proof = True
            else:
                issues.append("CC/Domínio Público sem Fonte/URL")

        if has_legal_proof:
            valid_legal_proof_count += 1

        # Adicionar à fila de pendências
        if issues or (not rec.license_type and not rec.legal_basis):
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
        'unlicensed_count': unlicensed_records.count(),
        'ai_generated_count': ai_generated_records.count(),
        'with_doc_count': records_with_doc.count(),
        'records_with_specs_count': records_with_specs_count,
        'attribution_rate': attribution_rate,
        'legal_proof_rate': legal_proof_rate,
        'license_distribution': license_distribution,
        'purpose_distribution': purpose_distribution,
        'legal_basis_distribution': legal_basis_distribution,
        'pending_records': pending_records[:100],
        'pending_total': len(pending_records),
    }

    return render(request, 'admin/copyright_audit.html', context)



@staff_member_required
def copyright_compliance_map(request):
    """
    Página do Mapa de Conformidade de Ativos Visuais.
    Calcula o percentual de conformidade de cada modelo da aplicação.
    """
    models_to_audit = [Book, Author, LiteraryUniverse, Article, Quiz, Event, Banner, Section]
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

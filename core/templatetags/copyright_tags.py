# core/templatetags/copyright_tags.py
"""
Template tags genéricas para o Sistema Corporativo de Governança de Ativos Visuais e Direitos Autorais.
Busca o ImageRightsRecord via ContentType + object_id + image_field_name e renderiza
atribuição pública sutil, padrão internacional TASL (Creative Commons) e botão de informações (ⓘ).
"""

import uuid
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.html import escape

from core.models.image_rights import ImageRightsRecord

register = template.Library()


@register.simple_tag
def render_image_rights(obj, field_name, show_info_icon=True):
    """
    Busca e renderiza os créditos do registro de direitos autorais de qualquer imagem.
    Sempre respeita o sigilo absoluto de informações privadas.
    """
    if not obj or not getattr(obj, 'pk', None):
        return ''

    try:
        ct = ContentType.objects.get_for_model(obj)
        record = ImageRightsRecord.objects.filter(
            content_type=ct,
            object_id=obj.pk,
            image_field_name=field_name
        ).first()
    except Exception:
        return ''

    if not record:
        return ''

    # Se não houver informação pública mínima para exibir
    if not record.credit_name and not record.work_title and not record.license_type:
        return ''

    parts = []
    license_display = record.get_license_type_display() if record.license_type else ''

    # 1. Atribuição do Título da Obra (se informado)
    if record.work_title:
        parts.append(f'<em>"{escape(record.work_title)}"</em>')

    # 2. Atribuição de Autor / Criador / Editora
    if record.credit_name:
        if record.source_url:
            parts.append(f'por <a href="{escape(record.source_url)}" target="_blank" rel="noopener noreferrer" class="text-decoration-underline text-secondary">{escape(record.credit_name)}</a>')
        else:
            parts.append(f'por {escape(record.credit_name)}')

    # 3. Padrão TASL para Creative Commons vs Outros Regimes
    if record.license_type == 'cc':
        if record.license_url:
            parts.append(f'(<a href="{escape(record.license_url)}" target="_blank" rel="noopener noreferrer" class="text-secondary fw-bold">Licença Creative Commons</a>)')
        else:
            parts.append('(Creative Commons)')
    elif record.license_type and record.license_type != 'own':
        parts.append(f'({escape(license_display)})')
    elif record.is_ai_generated:
        parts.append('(Criada por IA)')

    if not parts:
        return ''

    content_html = ' '.join(parts)
    icon_html = '<i class="fas fa-creative-commons me-1"></i>' if record.license_type == 'cc' else '<i class="fas fa-camera me-1"></i>'

    # Componente Informativo Opcional (ⓘ)
    modal_trigger_html = ''
    if show_info_icon:
        unique_modal_id = f"imgRightsModal_{uuid.uuid4().hex[:8]}"
        modal_trigger_html = f'''
        <button type="button" class="btn btn-link p-0 ms-1 text-secondary opacity-75" 
                style="font-size: 0.75rem; text-decoration: none;" 
                data-bs-toggle="modal" 
                data-bs-target="#{unique_modal_id}" 
                title="Informações da Imagem">
            <i class="fas fa-info-circle"></i>
        </button>

        <!-- Modal de Informações Públicas da Imagem -->
        <div class="modal fade" id="{unique_modal_id}" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-sm">
                <div class="modal-content text-start">
                    <div class="modal-header py-2 bg-light">
                        <h6 class="modal-header-title mb-0 font-weight-bold text-dark" style="font-size: 0.85rem;">
                            <i class="fas fa-shield-alt me-1 text-primary"></i> Informações da Imagem
                        </h6>
                        <button type="button" class="btn-close btn-sm" data-bs-dismiss="modal" aria-label="Fechar"></button>
                    </div>
                    <div class="modal-body py-3" style="font-size: 0.8rem; color: #2c3e50;">
                        {f'<div class="mb-2"><strong>Título da Obra:</strong> {escape(record.work_title)}</div>' if record.work_title else ''}
                        {f'<div class="mb-2"><strong>Autor / Detentor:</strong> {escape(record.credit_name)}</div>' if record.credit_name else ''}
                        {f'<div class="mb-2"><strong>Licença Jurídica:</strong> {escape(license_display)}</div>' if record.license_type else ''}
                        {f'<div class="mb-2"><strong>Gerada por IA:</strong> Sim</div>' if record.is_ai_generated else ''}
                        {f'<div class="mb-2"><strong>Fonte:</strong> <a href="{escape(record.source_url)}" target="_blank" rel="noopener noreferrer">Acessar Link Original</a></div>' if record.source_url else ''}
                        {f'<div class="mb-0"><strong>Termos da Licença:</strong> <a href="{escape(record.license_url)}" target="_blank" rel="noopener noreferrer">Ver Licença Oficial</a></div>' if record.license_url else ''}
                    </div>
                </div>
            </div>
        </div>
        '''

    html = f'''
    <div class="image-rights-credit text-secondary opacity-75 mt-1 d-inline-flex align-items-center flex-wrap justify-content-center" style="font-size: 0.73rem; line-height: 1.3;">
        <span>{icon_html}Arte / Crédito: {content_html}</span>
        {modal_trigger_html}
    </div>
    '''
    return mark_safe(html)

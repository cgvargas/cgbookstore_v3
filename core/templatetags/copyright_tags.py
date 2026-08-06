# core/templatetags/copyright_tags.py
"""
Template tags para renderização sutil de Atribuição TASL (Creative Commons)
e créditos de imagens nos templates públicos da CG.BookStore.
"""

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.html import escape

from core.models.image_rights import ImageRightsRecord

register = template.Library()


@register.simple_tag
def render_image_rights(obj, field_name):
    """
    Busca e renderiza os créditos do registro de direitos autorais para um determinado campo de imagem.
    Segue o padrão internacional TASL para Creative Commons.
    Apenas informações públicas são exibidas.
    """
    if not obj or not getattr(obj, 'pk', None):
        return ''

    ct = ContentType.objects.get_for_model(obj)
    record = ImageRightsRecord.objects.filter(
        content_type=ct,
        object_id=obj.pk,
        image_field_name=field_name
    ).first()

    if not record:
        return ''

    # Se não houver nada público informado
    if not record.credit_name and not record.work_title and not record.license_type:
        return ''

    parts = []

    # 1. Título da obra
    if record.work_title:
        parts.append(f'<em>"{escape(record.work_title)}"</em>')

    # 2. Autor / Criador
    if record.credit_name:
        if record.source_url:
            parts.append(f'por <a href="{escape(record.source_url)}" target="_blank" rel="noopener noreferrer" class="text-decoration-underline" style="color: inherit;">{escape(record.credit_name)}</a>')
        else:
            parts.append(f'por {escape(record.credit_name)}')

    # 3. Licença (com suporte TASL se for Creative Commons)
    if record.license_type == 'cc':
        if record.license_url:
            parts.append(f'(<a href="{escape(record.license_url)}" target="_blank" rel="noopener noreferrer" style="color: inherit;">Licença Creative Commons</a>)')
        else:
            parts.append('(Creative Commons)')
    elif record.license_type and record.license_type != 'own':
        parts.append(f'({escape(record.get_license_type_display())})')

    if not parts:
        return ''

    content_html = ' '.join(parts)
    icon_html = '<i class="fas fa-creative-commons me-1"></i>' if record.license_type == 'cc' else '<i class="fas fa-paint-brush me-1"></i>'

    html = f'''
    <div class="image-rights-credit text-secondary opacity-75 mt-1" style="font-size: 0.73rem; line-height: 1.3;">
        {icon_html}Arte / Crédito: {content_html}
    </div>
    '''
    return mark_safe(html)

"""
Widgets personalizados para o admin do Django
CG.BookStore v3
"""

from django import forms
from django.utils.safestring import mark_safe


class OpacitySliderWidget(forms.NumberInput):
    """
    Widget de slider para controlar opacidade de 0-100%
    Converte automaticamente de porcentagem (0-100) para decimal (0.0-1.0)
    """

    def __init__(self, attrs=None):
        default_attrs = {'class': 'opacity-slider-input', 'type': 'range', 'min': '0', 'max': '100', 'step': '1'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        """Converte valor decimal (0.0-1.0) para porcentagem (0-100)"""
        if value is None or value == '':
            return 100  # Padrão: 100% opaco
        try:
            return int(float(value) * 100)
        except (ValueError, TypeError):
            return 100

    def value_from_datadict(self, data, files, name):
        """Converte valor de porcentagem (0-100) para decimal (0.0-1.0)"""
        value = data.get(name)
        if value is None or value == '':
            return 1.0
        try:
            return float(value) / 100.0
        except (ValueError, TypeError):
            return 1.0

    def render(self, name, value, attrs=None, renderer=None):
        """Renderiza o widget com HTML customizado"""
        if value is None:
            value = 1.0

        percentage = self.format_value(value)
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs['name'] = name
        final_attrs['id'] = final_attrs.get('id', f'id_{name}')
        final_attrs['value'] = percentage

        html = f'''
        <div class="opacity-slider-container" style="max-width: 400px;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 8px;">
                <label for="{final_attrs['id']}" style="margin: 0; min-width: 120px; font-weight: 600;">
                    Opacidade: <span id="{final_attrs['id']}_value" style="color: #0066cc;">{percentage}%</span>
                </label>
                <input
                    type="range"
                    id="{final_attrs['id']}"
                    name="{name}"
                    min="0"
                    max="100"
                    step="1"
                    value="{percentage}"
                    style="flex: 1; height: 6px; cursor: pointer;"
                    oninput="document.getElementById('{final_attrs['id']}_value').textContent = this.value + '%'; document.getElementById('{final_attrs['id']}_preview').style.opacity = this.value / 100;"
                />
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #666; margin-bottom: 10px;">
                <span>0% (Transparente)</span>
                <span>100% (Opaco)</span>
            </div>
            <div id="{final_attrs['id']}_preview"
                 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        height: 60px;
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: 600;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        opacity: {percentage / 100};">
                Preview da Opacidade
            </div>
            <p class="help" style="margin-top: 8px; font-size: 12px; color: #666;">
                Arraste o controle para ajustar a transparência do container da seção.
                0% = Totalmente transparente, 100% = Totalmente opaco.
            </p>
        </div>
        '''

        return mark_safe(html)

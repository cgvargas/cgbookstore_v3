import os
import django
from django.conf import settings
from django.utils.html import format_html, conditional_escape

# Configuracao minima do Django para usar utilitarios
if not settings.configured:
    settings.configure()
    django.setup()

# Simular objeto e logica
class MockObj:
    def __init__(self, score):
        self.confidence_score = score

obj = MockObj(0.95)
color = "green"
label = "Alta"

print(f"Testing FIXED confidence_badge logic (Isolated)...")

try:
    # A correção aplicada foi: formatar ANTES de passar para format_html
    formatted_percentage = f"{obj.confidence_score:.0%}"
    
    result = format_html(
        '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} ({})</span>',
        color,
        label,
        formatted_percentage
    )
    
    print(f"Result: {result}")
    
    # Verificar se o resultado contem a porcentagem esperada e tags escapadas corretamente (embora aqui sejam strings simples)
    if "95%" in result and "span" in result:
        print("SUCCESS: Formatted correctly and no ValueError.")
    else:
        print("FAILURE: Unexpected output format.")
        
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

"""
Teste do modelo Gemini Pro.
"""
import os
import sys
import django

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

import google.generativeai as genai
from django.conf import settings

print("=" * 70)
print("TESTE DO MODELO GEMINI")
print("=" * 70)

# Configurar API
api_key = settings.GEMINI_API_KEY
print(f"\n✅ API Key: {api_key[:4]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

# Listar modelos disponíveis
print("\n📋 MODELOS DISPONÍVEIS:")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"   - {model.name}")
except Exception as e:
    print(f"   ❌ Erro ao listar modelos: {e}")

# Testar modelo gemini-pro
print("\n🧪 TESTANDO MODELO: gemini-pro")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Diga 'olá' em uma palavra")
    print(f"   ✅ Resposta: {response.text}")
    print(f"   ✅ Modelo gemini-pro está FUNCIONANDO!")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)

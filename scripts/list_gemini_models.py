"""
Script para listar todos os modelos disponíveis na API Google Gemini
"""
import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
import django
django.setup()

from django.conf import settings

def list_available_models():
    """Lista todos os modelos disponíveis na API Gemini"""

    print("=" * 70)
    print("  📋 LISTAGEM DE MODELOS DISPONÍVEIS - GOOGLE GEMINI AI")
    print("=" * 70)
    print()

    # Verificar se API Key está configurada
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("❌ GEMINI_API_KEY não está configurada no .env")
        return

    print(f"✅ API Key configurada: {api_key[:20]}***{api_key[-4:]}")
    print()

    try:
        import google.generativeai as genai
        print(f"✅ Biblioteca google-generativeai importada")

        # Verificar versão
        try:
            import importlib.metadata
            version = importlib.metadata.version('google-generativeai')
            print(f"📦 Versão da biblioteca: {version}")
        except:
            print("⚠️ Não foi possível determinar a versão da biblioteca")

        print()
        print("🔧 Configurando API Key...")
        genai.configure(api_key=api_key)
        print("✅ API Key configurada com sucesso")
        print()

        print("📡 Buscando modelos disponíveis...")
        print("=" * 70)

        models = genai.list_models()

        # Filtrar modelos que suportam generateContent
        generate_content_models = []

        for model in models:
            print(f"\n📌 Modelo: {model.name}")
            print(f"   Nome para uso: {model.name.replace('models/', '')}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Descrição: {model.description[:100] if model.description else 'N/A'}...")

            # Verificar métodos suportados
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
                print(f"   Métodos suportados: {', '.join(methods)}")

                if 'generateContent' in methods:
                    generate_content_models.append(model.name.replace('models/', ''))
                    print(f"   ✅ Suporta generateContent")

            print(f"   Limites de input: {model.input_token_limit if hasattr(model, 'input_token_limit') else 'N/A'} tokens")
            print(f"   Limites de output: {model.output_token_limit if hasattr(model, 'output_token_limit') else 'N/A'} tokens")

        print()
        print("=" * 70)
        print("  🎯 MODELOS RECOMENDADOS PARA generateContent")
        print("=" * 70)

        if generate_content_models:
            for i, model_name in enumerate(generate_content_models, 1):
                print(f"{i}. {model_name}")

            print()
            print("💡 Para usar no chatbot, edite gemini_service.py:")
            print(f"   self.model_name = '{generate_content_models[0]}'")
        else:
            print("⚠️ Nenhum modelo com suporte a generateContent encontrado")

        print()
        print("=" * 70)

    except ImportError as e:
        print(f"❌ Erro ao importar google.generativeai: {e}")
        print("   Instale com: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    list_available_models()

"""
Script para testar diferentes nomes de modelos Gemini e encontrar qual funciona
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

def test_models():
    """Testa diferentes nomes de modelos para encontrar o que funciona"""

    print("=" * 70)
    print("  🔍 TESTE DE MODELOS GEMINI - ENCONTRAR MODELO FUNCIONAL")
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

        # Verificar versão
        try:
            import importlib.metadata
            version = importlib.metadata.version('google-generativeai')
            print(f"📦 Versão da biblioteca: {version}")
        except:
            print("⚠️ Não foi possível determinar a versão da biblioteca")

        print()
        genai.configure(api_key=api_key)

        # Lista de modelos para testar
        models_to_test = [
            'gemini-pro',
            'gemini-1.0-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
            'gemini-2.0-flash-exp',
            'models/gemini-pro',
            'models/gemini-1.5-pro',
        ]

        print("🧪 Testando modelos disponíveis...\n")
        print("=" * 70)

        working_models = []
        test_message = "Olá! Responda apenas: OK"

        for model_name in models_to_test:
            print(f"\n📌 Testando: {model_name}")
            print("-" * 70)

            try:
                # Criar modelo
                model = genai.GenerativeModel(model_name)
                print(f"   ✅ Modelo inicializado")

                # Tentar gerar conteúdo
                response = model.generate_content(test_message)
                print(f"   ✅ Resposta recebida: {response.text[:50]}...")

                working_models.append(model_name)
                print(f"   🎉 SUCESSO! Este modelo funciona!")

            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    print(f"   ❌ Modelo não encontrado (404)")
                elif "403" in error_msg:
                    print(f"   ❌ Acesso negado (403)")
                elif "PERMISSION_DENIED" in error_msg:
                    print(f"   ❌ Sem permissão para este modelo")
                else:
                    print(f"   ❌ Erro: {error_msg[:100]}...")

        print()
        print("=" * 70)
        print("  📊 RESULTADO DOS TESTES")
        print("=" * 70)
        print()

        if working_models:
            print(f"✅ Encontrados {len(working_models)} modelo(s) funcional(is):\n")
            for i, model_name in enumerate(working_models, 1):
                print(f"   {i}. {model_name}")

            print()
            print("=" * 70)
            print("  🎯 RECOMENDAÇÃO")
            print("=" * 70)
            print()
            print(f"Use este modelo no gemini_service.py (linha 42):")
            print(f"   self.model_name = '{working_models[0]}'")
            print()
            print("Para aplicar automaticamente, execute:")
            print(f"   python scripts/update_model_name.py {working_models[0]}")
        else:
            print("❌ Nenhum modelo funcionou!")
            print()
            print("Possíveis causas:")
            print("1. API Key inválida ou expirada")
            print("2. Região não suportada")
            print("3. Versão da biblioteca incompatível")
            print()
            print("Tente:")
            print("1. Verificar a API Key em: https://aistudio.google.com/apikeys")
            print("2. Atualizar a biblioteca: pip install --upgrade google-generativeai")
            print("3. Criar uma nova API Key")

        print()
        print("=" * 70)

    except ImportError as e:
        print(f"❌ Erro ao importar google.generativeai: {e}")
        print("   Instale com: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_models()

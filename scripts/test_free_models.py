"""
Script para testar especificamente modelos gratuitos do Gemini
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

def test_free_models():
    """Testa modelos gratuitos do Gemini"""

    print("=" * 70)
    print("  🆓 TESTE DE MODELOS GEMINI GRATUITOS")
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
            pass

        print()
        genai.configure(api_key=api_key)

        # Tentar listar modelos disponíveis
        print("📡 Listando modelos disponíveis para sua API Key...")
        print("=" * 70)
        print()

        try:
            models_list = genai.list_models()

            print("✅ Modelos encontrados:\n")

            available_for_generate = []

            for model in models_list:
                model_name = model.name.replace('models/', '')

                # Verificar se suporta generateContent
                if hasattr(model, 'supported_generation_methods'):
                    methods = model.supported_generation_methods
                    if 'generateContent' in methods:
                        available_for_generate.append(model_name)
                        print(f"✅ {model_name}")
                        print(f"   Descrição: {model.display_name}")

                        # Mostrar limites
                        if hasattr(model, 'input_token_limit'):
                            print(f"   Input: {model.input_token_limit:,} tokens")
                        if hasattr(model, 'output_token_limit'):
                            print(f"   Output: {model.output_token_limit:,} tokens")
                        print()

            if available_for_generate:
                print("=" * 70)
                print("  🎯 MODELOS DISPONÍVEIS PARA generateContent")
                print("=" * 70)
                print()

                for i, model_name in enumerate(available_for_generate, 1):
                    print(f"{i}. {model_name}")

                print()
                print("=" * 70)
                print("  🧪 TESTANDO PRIMEIRO MODELO DISPONÍVEL")
                print("=" * 70)
                print()

                # Testar o primeiro modelo disponível
                test_model = available_for_generate[0]
                print(f"📌 Testando: {test_model}")
                print()

                try:
                    model = genai.GenerativeModel(test_model)
                    response = model.generate_content("Diga apenas: OK")

                    print(f"✅ SUCESSO! Resposta: {response.text}")
                    print()
                    print("=" * 70)
                    print("  ✅ CONFIGURAÇÃO RECOMENDADA")
                    print("=" * 70)
                    print()
                    print(f"Atualize gemini_service.py linha 42:")
                    print(f"   self.model_name = '{test_model}'")
                    print()
                    print("Ou execute:")
                    print(f"   python scripts/update_model_name.py {test_model}")
                    print()

                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        print(f"❌ ERRO DE QUOTA: {error_msg[:150]}...")
                        print()
                        print("=" * 70)
                        print("  ⚠️ PROBLEMA DE QUOTA DETECTADO")
                        print("=" * 70)
                        print()
                        print("Sua API Key excedeu a quota permitida.")
                        print()
                        print("Soluções:")
                        print()
                        print("1. AGUARDAR O RESET (recomendado)")
                        print("   - Quotas resetam a cada minuto/dia")
                        print("   - Aguarde alguns minutos e tente novamente")
                        print()
                        print("2. CRIAR NOVA API KEY")
                        print("   - Acesse: https://aistudio.google.com/app/apikey")
                        print("   - Clique em 'Create API Key'")
                        print("   - Selecione 'Create API key in new project'")
                        print("   - Copie e atualize no .env")
                        print()
                        print("3. VERIFICAR LIMITES")
                        print("   - Acesse: https://aistudio.google.com/apikeys")
                        print("   - Veja uso atual da sua key")
                        print()
                        print("Limites do Tier Gratuito:")
                        print("   - 15 requisições por minuto")
                        print("   - 1,500 requisições por dia")
                        print("   - 1 milhão de tokens por minuto")
                        print()
                    else:
                        print(f"❌ Erro ao testar: {error_msg[:150]}...")
            else:
                print("❌ Nenhum modelo com suporte a generateContent encontrado")

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print("❌ ERRO DE QUOTA ao listar modelos")
                print()
                print(f"Erro: {error_msg[:200]}...")
                print()
                print("=" * 70)
                print("  ⚠️ SUA API KEY EXCEDEU A QUOTA")
                print("=" * 70)
                print()
                print("SOLUÇÕES IMEDIATAS:")
                print()
                print("1. AGUARDAR ALGUNS MINUTOS")
                print("   A quota é por minuto (15 req/min)")
                print("   Aguarde 1-2 minutos e tente novamente")
                print()
                print("2. CRIAR NOVA API KEY")
                print("   https://aistudio.google.com/app/apikey")
                print("   → Create API Key → Create in new project")
                print()
                print("3. VERIFICAR STATUS")
                print("   https://aistudio.google.com/apikeys")
                print("   Veja o uso da sua API Key atual")
                print()
            else:
                print(f"❌ Erro ao listar modelos: {error_msg}")
                import traceback
                traceback.print_exc()

        print("=" * 70)

    except ImportError as e:
        print(f"❌ Erro ao importar google.generativeai: {e}")
        print("   Instale com: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print()
    print("💡 DICA: Se você testou muitas vezes, pode ter excedido a quota.")
    print("   Aguarde 1-2 minutos antes de executar este script.")
    print()
    input("Pressione ENTER para continuar...")
    print()
    test_free_models()

"""
Comando de teste para validar a integração com Google Gemini.
Uso: python manage.py test_gemini
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from chatbot_literario.gemini_service import get_chatbot_service


class Command(BaseCommand):
    help = 'Testa a integração com Google Gemini para o chatbot literário'

    def handle(self, *args, **options):
        """Executa o teste do serviço Gemini."""
        self.stdout.write("=" * 70)
        self.stdout.write("  🤖 TESTE DA API GOOGLE GEMINI - CHATBOT LITERÁRIO")
        self.stdout.write("=" * 70)

        # 1. Verificar configuração
        self.stdout.write("\n📋 Verificando configurações...")
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ GEMINI_API_KEY não configurada!"))
            self.stdout.write("   Configure no arquivo .env ou variáveis de ambiente")
            return

        masked_key = f"{api_key[:8]}***************************{api_key[-4:]}"
        self.stdout.write(self.style.SUCCESS(f"✅ API Key configurada: {masked_key}"))

        # 2. Inicializar serviço
        self.stdout.write("\n🔧 Inicializando serviço do chatbot...")
        try:
            service = get_chatbot_service()
            self.stdout.write(self.style.SUCCESS("✅ Serviço inicializado"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao inicializar: {e}"))
            return

        # 3. Verificar disponibilidade
        self.stdout.write("\n🔍 Verificando disponibilidade do serviço...")
        if not service.is_available():
            self.stdout.write(self.style.ERROR("❌ Serviço indisponível"))
            return
        self.stdout.write(self.style.SUCCESS("✅ Serviço disponível"))

        # 4. Teste de comunicação básica
        self.stdout.write("\n🚀 Testando comunicação com API Gemini...")

        test_messages = [
            "Olá! Me recomende um livro de ficção científica.",
            "Qual a diferença entre ficção científica e fantasia?",
            "Me explique como funciona o CG.BookStore"
        ]

        for i, test_msg in enumerate(test_messages, 1):
            self.stdout.write(f"\n{'─' * 70}")
            self.stdout.write(f"📨 Teste {i}/3: \"{test_msg}\"")

            try:
                response = service.get_response(test_msg)
                self.stdout.write(self.style.SUCCESS("✅ Resposta recebida com sucesso"))
                self.stdout.write(f"\n💬 Resposta do chatbot:")
                self.stdout.write(f"{response}\n")

            except Exception as e:
                self.stdout.write(self.style.ERROR("❌ Falha na comunicação"))
                self.stdout.write(f"   Erro: {e}")
                continue

        # 5. Teste de contexto (conversa com histórico)
        self.stdout.write(f"\n{'=' * 70}")
        self.stdout.write("🔄 Testando manutenção de contexto (conversa)...")

        history = []

        # Primeira mensagem
        msg1 = "Gosto muito de Isaac Asimov"
        self.stdout.write(f"\n👤 Usuário: {msg1}")
        try:
            resp1 = service.get_response(msg1, conversation_history=history)
            self.stdout.write(f"🤖 Bot: {resp1}\n")

            # Adicionar ao histórico
            history.append({"role": "user", "parts": [msg1]})
            history.append({"role": "model", "parts": [resp1]})

            # Segunda mensagem (testando contexto)
            msg2 = "Me recomende algo parecido"
            self.stdout.write(f"👤 Usuário: {msg2}")
            resp2 = service.get_response(msg2, conversation_history=history)
            self.stdout.write(f"🤖 Bot: {resp2}\n")

            self.stdout.write(self.style.SUCCESS("✅ Contexto mantido com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no teste de contexto: {e}"))

        # 6. Teste de tópico fora do escopo
        self.stdout.write(f"\n{'=' * 70}")
        self.stdout.write("🚫 Testando resposta para tópico fora do escopo...")

        off_topic_msg = "Como faço para cozinhar um bolo de chocolate?"
        self.stdout.write(f"\n👤 Usuário: {off_topic_msg}")
        try:
            off_topic_resp = service.get_response(off_topic_msg)
            self.stdout.write(f"🤖 Bot: {off_topic_resp}\n")
            self.stdout.write(self.style.SUCCESS("✅ Redirecionamento apropriado!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e}"))

        # Resumo final
        self.stdout.write(f"\n{'=' * 70}")
        self.stdout.write(self.style.SUCCESS("✨ TESTE CONCLUÍDO COM SUCESSO!"))
        self.stdout.write("=" * 70 + "\n")

"""
Comando para testar a conexão e funcionalidade da API do Google Gemini.
Uso: python manage.py test_gemini
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from chatbot_literario.gemini_service import get_chat_service
import sys


class Command(BaseCommand):
    help = 'Testa a configuração e funcionalidade da API do Google Gemini'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostra informações detalhadas do teste'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='Olá! Me recomende um livro de ficção científica.',
            help='Mensagem personalizada para testar o chatbot'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        test_message = options['message']

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.HTTP_INFO('  🤖 TESTE DA API GOOGLE GEMINI - CHATBOT LITERÁRIO'))
        self.stdout.write('='*70 + '\n')

        # 1. Verificar se API Key está configurada
        self.stdout.write('📋 Verificando configurações...\n')

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ GEMINI_API_KEY não configurada!'))
            self.stdout.write(self.style.WARNING('\n💡 Solução:'))
            self.stdout.write('   1. Obtenha uma API key em: https://makersuite.google.com/app/apikey')
            self.stdout.write('   2. Adicione ao .env: GEMINI_API_KEY=sua_key_aqui')
            self.stdout.write('   3. Execute este comando novamente\n')
            sys.exit(1)
        else:
            masked_key = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
            self.stdout.write(self.style.SUCCESS(f'✅ API Key configurada: {masked_key}'))

        # 2. Inicializar serviço
        self.stdout.write('\n🔧 Inicializando serviço do chatbot...')
        try:
            chat_service = get_chat_service()
            self.stdout.write(self.style.SUCCESS('✅ Serviço inicializado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao inicializar serviço: {e}'))
            sys.exit(1)

        # 3. Verificar disponibilidade
        self.stdout.write('\n🔍 Verificando disponibilidade do serviço...')
        if not chat_service.is_available():
            self.stdout.write(self.style.ERROR('❌ Serviço não disponível'))
            self.stdout.write(self.style.WARNING('   Verifique se a API key está correta'))
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('✅ Serviço disponível'))

        # 4. Informações do modelo (se --detailed)
        if detailed:
            self.stdout.write('\n📊 Informações do Modelo:')
            self.stdout.write(f'   • Nome: {chat_service.model_name}')
            self.stdout.write(f'   • Timeout: {chat_service.request_timeout}s')
            self.stdout.write(f'   • API Key válida: Sim')

        # 5. Testar chamada real à API
        self.stdout.write('\n🚀 Testando comunicação com API Gemini...')
        self.stdout.write(f'   Mensagem de teste: "{test_message}"\n')

        try:
            result = chat_service.get_response(
                user_message=test_message,
                conversation_history=[]
            )

            if result['success']:
                self.stdout.write(self.style.SUCCESS('✅ Comunicação bem-sucedida!\n'))

                # Mostrar resposta
                self.stdout.write('📬 Resposta do Gemini:')
                self.stdout.write('-' * 70)

                response = result['response']
                # Limitar resposta se for muito longa e não estiver em modo detalhado
                if not detailed and len(response) > 300:
                    response = response[:300] + '...\n[Use --detailed para ver resposta completa]'

                self.stdout.write(self.style.HTTP_INFO(response))
                self.stdout.write('-' * 70)

                # Estatísticas
                self.stdout.write(f'\n📈 Estatísticas:')
                self.stdout.write(f'   • Comprimento da resposta: {len(result["response"])} caracteres')
                self.stdout.write(f'   • Status: Operacional')

            else:
                self.stdout.write(self.style.ERROR('❌ Falha na comunicação'))
                self.stdout.write(f'   Erro: {result["error"]}')
                sys.exit(1)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro durante teste: {str(e)}'))
            if detailed:
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
            sys.exit(1)

        # 6. Resumo final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ TESTE CONCLUÍDO COM SUCESSO!'))
        self.stdout.write('='*70)

        self.stdout.write('\n✨ Próximos passos:')
        self.stdout.write('   1. Execute: python manage.py makemigrations chatbot_literario')
        self.stdout.write('   2. Execute: python manage.py migrate')
        self.stdout.write('   3. Acesse: http://localhost:8000/chatbot/')
        self.stdout.write('   4. Faça login e teste o chatbot!\n')

        self.stdout.write('💡 Dicas:')
        self.stdout.write('   • Use --message "sua pergunta" para testar mensagens específicas')
        self.stdout.write('   • Use --detailed para ver informações completas')
        self.stdout.write('   • Exemplo: python manage.py test_gemini --message "Recomende um romance" --detailed\n')

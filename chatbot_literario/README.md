# 📚 Chatbot Literário - Assistente de Recomendações de Livros

Sistema de chatbot conversacional integrado com Google Gemini AI para fornecer recomendações personalizadas de livros e discussões sobre literatura.

## 🎯 Funcionalidades

- **Conversação Natural**: Interface de chat em tempo real com respostas contextuais
- **Recomendações Personalizadas**: Sugestões de livros baseadas nas preferências do usuário
- **Histórico de Conversas**: Persistência de mensagens com sessões por usuário
- **Integração com Catálogo**: Acesso ao catálogo completo da CG.BookStore
- **Interface Moderna**: UI responsiva com animações e indicadores de digitação
- **Diagnóstico Integrado**: Ferramentas para verificar status da API e configuração

## 🏗️ Arquitetura

### Componentes Principais

```
chatbot_literario/
├── models.py                    # Modelo ChatConversation para persistência
├── gemini_service.py            # Serviço de integração com Google Gemini AI
├── views.py                     # Views e API endpoints
├── urls.py                      # Configuração de rotas
├── admin.py                     # Interface administrativa
├── management/
│   └── commands/
│       └── test_gemini.py      # Comando CLI para diagnóstico
├── templates/
│   └── chatbot_literario/
│       ├── chat.html           # Interface de chat
│       └── diagnostic.html     # Página de diagnóstico
├── TROUBLESHOOTING.md          # Guia de resolução de problemas
└── README.md                   # Este arquivo
```

### Fluxo de Dados

```
Usuário → Interface Chat → API Endpoint → GeminiChatService
                                               ↓
                                          Google Gemini AI
                                               ↓
                                          Resposta → ChatConversation (DB)
                                               ↓
                                          Interface Chat → Usuário
```

## 🚀 Configuração

### 1. Requisitos

- Python 3.11+
- Django 5.1.1+
- Google Gemini API Key (gratuita em https://ai.google.dev/)
- PostgreSQL (Supabase)

### 2. Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Google Gemini AI
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Importante:**
- Não use aspas ao redor da chave
- Não adicione espaços antes ou depois do `=`
- A chave deve começar com `AIzaSy`

### 3. Instalação

```bash
# 1. Instalar dependências
pip install google-generativeai==0.8.5

# 2. Executar migrações
python manage.py makemigrations chatbot_literario
python manage.py migrate

# 3. Testar configuração
python manage.py test_gemini
```

### 4. Verificar Instalação

```bash
# Teste via comando CLI
python manage.py test_gemini

# Ou acesse a página de diagnóstico
# http://localhost:8000/chatbot/diagnostic/
```

## 📖 Uso

### Interface Web

1. **Acesse o chatbot**: `http://localhost:8000/chatbot/`
2. **Faça login**: Requer autenticação de usuário
3. **Converse**: Digite mensagens no campo de input
4. **Histórico**: Suas conversas são salvas automaticamente

### API Endpoints

#### 1. Enviar Mensagem
```http
POST /chatbot/api/send/
Content-Type: application/json

{
  "message": "Me recomende um livro de ficção científica",
  "session_id": "uuid-da-sessao"
}
```

**Resposta:**
```json
{
  "success": true,
  "response": "Olá! Com base em suas preferências...",
  "error": null
}
```

#### 2. Obter Histórico
```http
GET /chatbot/api/history/?session_id=uuid-da-sessao
```

**Resposta:**
```json
{
  "success": true,
  "messages": [
    {
      "role": "user",
      "message": "Olá!",
      "created_at": "2024-11-22T10:00:00Z"
    },
    {
      "role": "assistant",
      "message": "Olá! Como posso ajudar?",
      "created_at": "2024-11-22T10:00:01Z"
    }
  ]
}
```

#### 3. Limpar Histórico
```http
POST /chatbot/api/clear/
Content-Type: application/json

{
  "session_id": "uuid-da-sessao"
}
```

#### 4. Verificar Status
```http
GET /chatbot/api/check/
```

**Resposta:**
```json
{
  "available": true,
  "model": "gemini-1.5-pro",
  "api_key_configured": true
}
```

### Comando CLI

```bash
# Teste básico
python manage.py test_gemini

# Teste detalhado
python manage.py test_gemini --detailed

# Teste com mensagem personalizada
python manage.py test_gemini --message "Qual seu livro favorito?"
```

## 🔧 Configuração Avançada

### GeminiChatService

O serviço pode ser configurado em `gemini_service.py`:

```python
class GeminiChatService:
    def __init__(self):
        # Modelo utilizado (pode ser alterado)
        self.model_name = 'gemini-1.5-pro'

        # Timeout para requisições
        self.request_timeout = 30
```

### Modelos Disponíveis

| Modelo | Características | Recomendação |
|--------|----------------|--------------|
| `gemini-1.5-pro` | Mais capaz e estável | ✅ **Recomendado** |
| `gemini-1.5-flash-latest` | Mais rápido | ⚡ Para respostas rápidas |
| `gemini-pro` | Versão anterior | 📦 Legado |

### Parâmetros de Geração

Configurados em `generation_config`:

```python
generation_config = {
    'temperature': 0.9,        # Criatividade (0.0 - 1.0)
    'top_p': 0.95,            # Núcleo de probabilidade
    'top_k': 40,              # Top-k sampling
    'max_output_tokens': 1024, # Tamanho máximo da resposta
}
```

**Ajustes recomendados:**
- `temperature` baixo (0.3-0.5): Respostas mais precisas e consistentes
- `temperature` alto (0.8-1.0): Respostas mais criativas e variadas
- `max_output_tokens`: Limite de tamanho (1024 = ~750 palavras)

### System Prompt

O comportamento do chatbot é definido em `_build_system_prompt()`. Para personalizar:

```python
def _build_system_prompt(self):
    """Customizar o prompt do sistema aqui"""
    return """Você é um assistente literário especializado..."""
```

## 🧪 Testes

### Teste Manual (Navegador)

1. Acesse `http://localhost:8000/chatbot/`
2. Envie mensagem: "Olá!"
3. Verifique resposta do chatbot
4. Teste diferentes perguntas sobre livros

### Teste Automatizado (CLI)

```bash
# Teste completo com todos os checks
python manage.py test_gemini --detailed
```

**Checklist de Testes:**
- ✅ API Key configurada
- ✅ Serviço inicializado
- ✅ Modelo carregado
- ✅ Resposta de teste recebida
- ✅ Histórico persistido no banco

### Teste de Diagnóstico (Web)

Acesse: `http://localhost:8000/chatbot/diagnostic/`

**Verifica:**
- Status da API Key
- Modelo configurado
- Serviço disponível
- Inicialização bem-sucedida
- Estatísticas de uso

## 🐛 Resolução de Problemas

### Erro: "Unknown command: 'test_gemini'"

**Causa:** Cache do Python não atualizado

**Solução:**
```bash
# Windows
.\scripts\clear_cache.bat

# Linux/Mac
./scripts/clear_cache.sh

# Manual
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

### Erro: "404 models/gemini-1.5-flash is not found"

**Causa:** Modelo incorreto especificado

**Solução:** Atualizar para a versão mais recente
```bash
git pull origin claude/claude-md-miakpd81q0f8rkob-01Sem7nU9FQwRPXw3zErpnx1
```

Ou editar manualmente `gemini_service.py` linha 42:
```python
self.model_name = 'gemini-1.5-pro'  # ✅ Correto
```

### Erro: "API Key not configured"

**Solução:**
1. Verificar arquivo `.env` existe na raiz
2. Verificar variável `GEMINI_API_KEY` está definida
3. Reiniciar servidor Django
4. Testar: `python manage.py test_gemini`

### Chatbot não responde

**Diagnóstico:**
```bash
# 1. Verificar logs do Django
# No terminal onde runserver está executando

# 2. Verificar página de diagnóstico
# http://localhost:8000/chatbot/diagnostic/

# 3. Testar API diretamente
python manage.py test_gemini --detailed
```

**Soluções comuns:**
- Verificar conexão com internet
- Validar API Key no Google AI Studio
- Verificar quota da API (1000 req/dia no tier gratuito)
- Revisar logs para exceções

## 📊 Modelos de Dados

### ChatConversation

```python
class ChatConversation(models.Model):
    user = ForeignKey(User)              # Usuário da conversa
    role = CharField(max_length=10)      # 'user' ou 'assistant'
    message = TextField()                # Conteúdo da mensagem
    created_at = DateTimeField()         # Timestamp
    session_id = CharField(max_length=100)  # ID da sessão
```

**Índices:**
- `user` + `created_at` (para consultas de histórico)
- `session_id` (para filtrar por sessão)

**Métodos úteis:**
```python
# Obter histórico do usuário
ChatConversation.get_user_history(user, limit=20, session_id=None)

# Buscar conversas recentes
ChatConversation.objects.filter(
    user=user,
    created_at__gte=timezone.now() - timedelta(days=7)
)
```

## 🔒 Segurança

### Proteção de Rotas

Todas as views requerem autenticação:

```python
@login_required
def chat_view(request):
    # Apenas usuários autenticados
    pass
```

### Proteção da API Key

- **Nunca** commitar `.env` no git
- Usar variáveis de ambiente em produção
- Mascarar key nos logs e interface (`AIzaSyBZ***Pvu4`)

### Validação de Input

```python
# Limitar tamanho de mensagens
if len(user_message) > 5000:
    return JsonResponse({'error': 'Mensagem muito longa'}, status=400)

# Sanitizar HTML
from django.utils.html import escape
clean_message = escape(user_message)
```

## 📈 Performance

### Caching

O serviço usa lazy loading para evitar timeouts:

```python
@property
def model(self):
    """Carrega modelo apenas quando necessário"""
    if self._model:
        return self._model
    # Inicializa modelo aqui
```

### Otimizações

- **Histórico limitado**: Apenas últimas 10 mensagens para contexto
- **Singleton service**: Uma instância do serviço reutilizada
- **Índices de banco**: Em `user`, `created_at`, `session_id`

### Limites da API

Google Gemini API Free Tier:
- **Requisições**: 1000/dia
- **Rate limit**: 100/100 segundos
- **Tokens**: ~32k input, ~8k output por requisição

## 🎨 Customização da Interface

### Cores e Tema

Editar `templates/chatbot_literario/chat.html`:

```css
.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Alterar gradiente aqui */
}

.message.user .message-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Cor das mensagens do usuário */
}
```

### Mensagem de Boas-vindas

```html
<div class="welcome-message">
    <i class="fas fa-book-reader"></i>
    <h4>Olá! Sou seu assistente literário 📚</h4>
    <p>Personalize esta mensagem aqui!</p>
</div>
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente (Render.com)

```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX
DEBUG=False
ALLOWED_HOSTS=cgbookstore-v3.onrender.com
```

### Checklist de Deploy

- [ ] API Key configurada no Render
- [ ] Migrações executadas (`python manage.py migrate`)
- [ ] Static files coletados (`collectstatic`)
- [ ] Testar endpoint `/chatbot/api/check/`
- [ ] Verificar logs para erros
- [ ] Testar interface `/chatbot/`

## 📚 Recursos Adicionais

### Documentação

- **Google Gemini AI**: https://ai.google.dev/docs
- **Django**: https://docs.djangoproject.com/
- **TROUBLESHOOTING.md**: Guia completo de problemas comuns

### Links Úteis

- **Obter API Key**: https://ai.google.dev/
- **Google AI Studio**: https://aistudio.google.com/
- **Gemini API Reference**: https://ai.google.dev/api/python/google/generativeai

## 🤝 Contribuindo

### Estrutura de Commits

```bash
git commit -m "Feature: Adicionar funcionalidade X"
git commit -m "Fix: Corrigir erro Y"
git commit -m "Docs: Atualizar documentação Z"
```

### Workflow de Desenvolvimento

1. Criar branch: `git checkout -b feature/nome-feature`
2. Desenvolver e testar localmente
3. Commitar mudanças
4. Push e criar PR

## 📝 Changelog

### v1.0.0 (2024-11-22)

#### Implementado
- ✅ Integração completa com Google Gemini AI
- ✅ Interface de chat em tempo real
- ✅ Persistência de histórico de conversas
- ✅ Sistema de sessões por usuário
- ✅ Comando CLI para diagnóstico (`test_gemini`)
- ✅ Página web de diagnóstico
- ✅ 4 endpoints de API REST
- ✅ Interface administrativa
- ✅ Documentação completa

#### Corrigido
- ✅ Modelo Gemini corrigido de `gemini-1.5-flash` para `gemini-1.5-pro`
- ✅ Lazy loading para evitar timeout no Gunicorn
- ✅ Cache clearing scripts para Windows e Linux

#### Conhecido
- ⚠️ Supabase DNS pode gerar warnings (não afeta funcionamento)
- ⚠️ Quota limitada no tier gratuito do Gemini (1000 req/dia)

---

## 📧 Suporte

Para problemas ou dúvidas:

1. **Consulte**: `TROUBLESHOOTING.md`
2. **Teste**: `python manage.py test_gemini --detailed`
3. **Diagnóstico**: `http://localhost:8000/chatbot/diagnostic/`
4. **Logs**: Verificar output do `runserver` ou logs do Render

---

**Desenvolvido para CG.BookStore v3** | Powered by Google Gemini AI 🤖📚

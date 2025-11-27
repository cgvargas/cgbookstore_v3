# 🚀 Como Configurar Groq AI no Chatbot

O **Groq** é uma alternativa **gratuita, rápida e poderosa** ao Google Gemini para o chatbot literário da CG.BookStore.

## ✨ Por Que Usar Groq?

| Característica | Groq | Gemini |
|----------------|------|--------|
| **Velocidade** | ⚡ Extremamente rápido (hardware especializado) | 🐢 Médio |
| **Free Tier** | ✅ 14.400 requisições/dia | ⚠️ Limitado (facilmente ultrapassado) |
| **Limite de Taxa** | ✅ 7.200 tokens/minuto | ⚠️ Muito baixo |
| **Cartão de Crédito** | ❌ Não requer | ✅ Requer para aumentar limites |
| **Modelos** | 🤖 Llama 3.1 70B, Mixtral, Gemma 2 | 🤖 Gemini 2.0 Flash |
| **Custo** | 💰 Grátis ilimitado (free tier) | 💰 Grátis com limites rígidos |

---

## 📋 Passos para Configurar

### 1. Criar Conta no Groq

1. Acesse: **https://console.groq.com**
2. Clique em **"Sign Up"** ou **"Get Started"**
3. Crie sua conta (pode usar conta Google/GitHub)
4. **Não precisa de cartão de crédito!** ✅

### 2. Obter API Key

1. Faça login em: **https://console.groq.com**
2. No menu lateral, clique em **"API Keys"**
3. Clique em **"Create API Key"**
4. Dê um nome (ex: "CG.BookStore Chatbot")
5. **Copie a chave** - você não poderá vê-la novamente!

Exemplo de API Key:
```
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Configurar no Projeto

#### **No arquivo `.env`:**

Abra o arquivo `.env` e adicione sua chave Groq:

```env
# AI Provider Configuration
AI_PROVIDER=groq

# Groq AI Configuration
GROQ_API_KEY=gsk_sua_chave_aqui_xxxxxxxxxxxxxxxxx
```

⚠️ **IMPORTANTE:** Substitua `gsk_sua_chave_aqui_xxxxxxxxxxxxxxxxx` pela sua chave real!

### 4. Instalar Dependência (Se ainda não instalou)

No PowerShell/Terminal:

```powershell
# Windows
pip install groq

# Linux/Mac
pip3 install groq
```

Ou instale todas as dependências:

```powershell
pip install -r requirements.txt
```

### 5. Testar o Chatbot

1. Inicie o servidor:
   ```powershell
   python manage.py runserver
   ```

2. Acesse: **http://localhost:8000**

3. Faça login na aplicação

4. Clique no widget flutuante do Dbit (canto inferior direito)

5. Envie uma mensagem de teste:
   ```
   Olá Dbit! Pode me recomendar um livro de fantasia?
   ```

6. A resposta deve chegar **muito mais rápida** que com Gemini! ⚡

---

## 🔄 Alternar Entre Groq e Gemini

Você pode alternar facilmente entre os provedores de IA editando o `.env`:

### Usar Groq (Recomendado):
```env
AI_PROVIDER=groq
GROQ_API_KEY=gsk_sua_chave_aqui
```

### Usar Gemini:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_gemini_aqui
```

**Reinicie o servidor** após alterar o provedor!

---

## 🎯 Modelos Disponíveis no Groq

O chatbot está configurado para usar **`llama-3.1-70b-versatile`** (recomendado).

Outros modelos disponíveis (se quiser experimentar, edite `groq_service.py`):

| Modelo | Descrição | Uso |
|--------|-----------|-----|
| `llama-3.1-70b-versatile` | ⭐ Mais inteligente (70B parâmetros) | **Recomendado para chatbot** |
| `llama-3.1-8b-instant` | ⚡ Mais rápido (8B parâmetros) | Respostas instantâneas |
| `mixtral-8x7b-32768` | 📚 Contexto longo (32K tokens) | Conversas longas |
| `gemma2-9b-it` | 🎯 Eficiente e rápido | Bom equilíbrio |

---

## 📊 Limites do Free Tier

### Groq Free Tier (Muito Generoso):
- ✅ **14.400 requisições por dia**
- ✅ **7.200 tokens por minuto**
- ✅ **Sem necessidade de cartão de crédito**
- ✅ **Velocidade extremamente rápida**

### Comparação com Gemini Free:
- ⚠️ Gemini: ~15 requisições por minuto (900/hora)
- ⚠️ Fácil de ultrapassar com múltiplos usuários
- ⚠️ Precisa criar múltiplas contas ou pagar

---

## 🛠️ Troubleshooting

### Erro: "GROQ_API_KEY não configurada"
✅ **Solução:** Verifique se você adicionou a chave no `.env` corretamente

### Erro: "401 Unauthorized"
✅ **Solução:** Sua API Key está incorreta ou expirou. Crie uma nova em https://console.groq.com

### Erro: "429 Rate Limit Exceeded"
✅ **Solução:** Você ultrapassou o limite (raro). Aguarde 1 minuto e tente novamente.

### Chatbot ainda usa Gemini
✅ **Solução:**
1. Verifique se `AI_PROVIDER=groq` no `.env`
2. Reinicie o servidor
3. Limpe o cache do navegador (Ctrl+Shift+Delete)

### Respostas muito lentas
✅ **Solução:**
- Groq é extremamente rápido. Se estiver lento, pode ser sua conexão.
- Tente trocar o modelo para `llama-3.1-8b-instant` em `groq_service.py`

---

## 🎉 Pronto!

Seu chatbot agora usa o **Groq AI** - muito mais rápido e com free tier generoso!

### Vantagens que você terá:
- ⚡ **Respostas 5-10x mais rápidas**
- ✅ **14.400 requisições/dia** (vs ~900/hora do Gemini)
- 💰 **Completamente gratuito**
- 🚀 **Sem limites frustrantes**

### Quer voltar para Gemini?
Basta mudar `AI_PROVIDER=gemini` no `.env` e reiniciar o servidor!

---

## 📞 Suporte

- **Documentação Groq:** https://console.groq.com/docs
- **Modelos disponíveis:** https://console.groq.com/docs/models
- **Status da API:** https://status.groq.com
- **Fórum:** https://console.groq.com/forum

---

## 🔐 Segurança

⚠️ **NUNCA** compartilhe sua `GROQ_API_KEY`!
⚠️ **NUNCA** commit o arquivo `.env` no Git!
✅ O `.env` já está no `.gitignore` - suas chaves estão seguras!

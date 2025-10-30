# 🎯 Fluxo Simplificado: Recomendações com IA

## Visão Resumida

```
👤 USUÁRIO
   |
   | [Clica "IA Premium"]
   ↓
🌐 NAVEGADOR (JavaScript)
   |
   | GET /api/recommendations/?algorithm=ai&limit=6
   ↓
🔧 BACKEND (views_simple.py)
   |
   | 1. Busca histórico: "Quais livros o usuário leu?"
   |    → UserBookInteraction (últimas 20)
   |
   ↓
🤖 GEMINI AI (gemini_ai.py)
   |
   | 2. Monta prompt:
   |    "Usuário leu: Tolkien, Harry Potter, Mangá
   |     Gêneros favoritos: Fantasia
   |     Recomende 6 livros similares com justificativas"
   |
   | 3. Chama API Google Gemini 2.5 Flash
   |    ⏱️ ~3-5 segundos
   |
   | 4. Gemini retorna:
   |    [
   |      {"title": "O Hobbit", "author": "Tolkien",
   |       "reason": "Porta de entrada para Terra Média..."},
   |      {"title": "Duna", "author": "Herbert",
   |       "reason": "Ficção épica com worldbuilding..."},
   |      {"title": "A Odisseia", ...},
   |      ...
   |    ]
   |
   ↓
🔍 VALIDAÇÃO (views_simple.py)
   |
   | 5. Para cada livro recomendado pela IA:
   |
   |    "O Hobbit" → Existe no banco? ✅ SIM → Adiciona
   |    "Duna" → Existe no banco? ❌ NÃO → Ignora
   |    "A Odisseia" → Existe? ❌ NÃO → Ignora
   |    "O Nome do Vento" → Existe? ✅ SIM → Adiciona
   |
   | 6. Resultado: 2 livros REAIS (com imagens)
   |
   ↓
📦 RESPOSTA JSON
   |
   | {
   |   "algorithm": "ai",
   |   "count": 2,
   |   "recommendations": [
   |     {
   |       "id": 2,
   |       "slug": "o-hobbit-edicao-ilustrada",
   |       "title": "O Hobbit em quadrinhos",
   |       "author": "J.R.R. Tolkien",
   |       "cover_image": "https://supabase.co/.../hobbit.jpg",
   |       "score": 0.95,
   |       "reason": "Porta de entrada perfeita..."
   |     },
   |     {
   |       "id": 45,
   |       "slug": "o-nome-do-vento",
   |       "title": "O Nome do Vento",
   |       "author": "Patrick Rothfuss",
   |       "cover_image": "https://supabase.co/.../vento.jpg",
   |       "score": 0.95,
   |       "reason": "Fantasia moderna com prosa lírica..."
   |     }
   |   ]
   | }
   |
   ↓
🌐 NAVEGADOR (JavaScript)
   |
   | 7. Renderiza 2 cards com:
   |    - Imagem da capa (Supabase)
   |    - Título e autor
   |    - Badge "95%"
   |    - Justificativa da IA
   |    - Botão "Ver livro"
   |
   ↓
👤 USUÁRIO VÊ RECOMENDAÇÕES! 🎉
```

---

## 🎯 Por que só 2 livros ao invés de 6?

**Gemini recomendou 6 livros:**
1. ✅ O Hobbit → Existe no banco → **Mostra**
2. ❌ A Sociedade do Anel → Não existe → **Ignora**
3. ❌ Um Mago de Terramar → Não existe → **Ignora**
4. ❌ Duna → Não existe → **Ignora**
5. ✅ O Nome do Vento → Existe no banco → **Mostra**
6. ❌ A Odisseia → Não existe → **Ignora**

**Resultado:** Apenas 2 livros existem no catálogo!

---

## 💡 Solução: Expandir Catálogo

Para melhorar as recomendações da IA:

1. **Adicionar mais livros ao banco de dados**
   - Cadastrar "Duna", "A Odisseia", etc.

2. **IA aprenderá o catálogo** (futura melhoria)
   - Passar lista de livros disponíveis no prompt
   - Gemini recomendará APENAS livros do catálogo

3. **Fallback automático**
   - Se nenhum livro for encontrado
   - Sistema usa algoritmo Híbrido automaticamente

---

## ⚡ Cache = Performance

**Primeira vez (sem cache):**
```
Usuário → API → Gemini (~5s) → Validação → Resposta
Total: ~5-6 segundos
```

**Segunda vez (com cache):**
```
Usuário → API → Cache (100ms) → Validação → Resposta
Total: ~200ms (25x mais rápido!)
```

Cache expira em 1 hora. Depois disso, chama Gemini novamente.

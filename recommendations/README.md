# Sistema de Recomendações Inteligente 📚✨

Sistema completo de recomendações de livros usando Machine Learning e Google Gemini AI.

## Status: ✅ FUNCIONAL

```
Testes: 5/6 passando (83%)
Algoritmos: 4 implementados
API: 6 endpoints ativos
Docs: Completa
```

## Quick Start

### 1. Testar o Sistema

```bash
python test_recommendations.py
```

### 2. Usar a API

```javascript
// Obter recomendações híbridas
fetch('/recommendations/api/recommendations/?algorithm=hybrid&limit=10')
    .then(res => res.json())
    .then(data => console.log(data.recommendations));

// Livros similares
fetch('/recommendations/api/books/42/similar/?limit=5')
    .then(res => res.json())
    .then(data => console.log(data.similar_books));
```

### 3. Incluir no Template

```django
{% include 'recommendations/recommendations_section.html' %}
```

## Algoritmos Disponíveis

1. **Collaborative Filtering** - Baseado em usuários similares
2. **Content-Based** - TF-IDF + Cosine Similarity
3. **Hybrid** - Combina todos os métodos (recomendado)
4. **Gemini AI** - Recomendações com IA (requer API key)

## Endpoints da API

```
GET  /recommendations/api/recommendations/      # Obter recomendações
GET  /recommendations/api/books/{id}/similar/   # Livros similares
POST /recommendations/api/interactions/         # Registrar interação
GET  /recommendations/api/profile/me/           # Perfil do usuário
GET  /recommendations/api/insights/             # Insights com IA
```

## Configuração Opcional

### Adicionar API Key do Gemini

```bash
# .env
GEMINI_API_KEY=sua_chave_aqui
```

Obtenha em: https://makersuite.google.com/app/apikey

> O sistema funciona perfeitamente sem a API key - você terá acesso aos 3 outros algoritmos.

## Arquitetura

```
recommendations/
├── models.py           # 4 modelos (UserProfile, Interaction, Similarity, Recommendation)
├── algorithms.py       # 3 algoritmos ML (Collaborative, Content, Hybrid)
├── gemini_ai.py       # Integração Gemini AI
├── views.py           # 6 endpoints REST
├── serializers.py     # 7 serializers
├── tasks.py           # 5 tasks Celery
├── urls.py            # Rotas configuradas
└── admin.py           # Admin registrado
```

## Features

- ✅ 4 algoritmos de recomendação
- ✅ API REST completa
- ✅ Machine Learning (TF-IDF)
- ✅ Integração com Gemini AI
- ✅ Cache inteligente (Redis)
- ✅ Processamento assíncrono (Celery)
- ✅ Rate limiting
- ✅ 11 índices de banco de dados
- ✅ Frontend responsivo
- ✅ Testes automatizados

## Documentação Completa

Ver `/documents/Projetos Modulares/recomendacoes_ia/`:

- `COMO_USAR_RECOMENDACOES.md` - Guia prático de uso
- `SISTEMA_RECOMENDACOES_IA.md` - Documentação técnica completa
- `IMPLEMENTACAO_COMPLETA.md` - Relatório de implementação
- `STATUS_SISTEMA_RECOMENDACOES_28102025.md` - Status atual

## Exemplos

### Registrar Interação

```python
from recommendations.models import UserBookInteraction

UserBookInteraction.objects.create(
    user=request.user,
    book=book,
    interaction_type='read',
    rating=5
)
```

### Obter Recomendações Programaticamente

```python
from recommendations.algorithms import HybridRecommendationSystem

engine = HybridRecommendationSystem()
recommendations = engine.recommend(user, n=10)

for rec in recommendations:
    print(f"{rec['book'].title} - Score: {rec['score']:.2f}")
```

### Executar Task Celery

```python
from recommendations.tasks import compute_book_similarities

# Executar agora
result = compute_book_similarities.delay()

# Verificar resultado
print(result.get())
```

## Rate Limiting

- GET /recommendations/: **30 req/h** por usuário
- GET /similar/: **50 req/h** por usuário
- POST /interactions/: **100 req/h** por usuário

## Cache Strategy

- Recomendações: **1 hora**
- Similaridades: **24 horas**
- Vetores TF-IDF: **24 horas**
- Trending books: **6 horas**

## Tasks Celery Agendadas

- **Similaridades:** Diariamente às 3h
- **Recomendações batch:** A cada hora
- **Limpeza:** Diariamente às 4h
- **Trending:** A cada 6 horas

## Troubleshooting

### "No recommendations generated"
- Usuário precisa de pelo menos 5 interações
- Ou use `algorithm=content` (funciona desde primeira interação)

### "Gemini AI não configurado"
- Adicione GEMINI_API_KEY ao .env
- Ou use outros algoritmos (hybrid, collaborative, content)

### Cache não funciona
- Verifique se Redis está rodando: `redis-cli ping`
- Deve retornar: `PONG`

## Contribuindo

Sistema desenvolvido com Django 5.0.3, DRF 3.16.1, scikit-learn 1.7.2 e Google Gemini AI.

## Licença

Parte do projeto CGBookStore v3.

---

**Versão:** 1.0.0
**Status:** Produção
**Última atualização:** 28/10/2025

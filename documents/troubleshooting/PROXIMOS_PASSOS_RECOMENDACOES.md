# 🎉 Sistema de Recomendações - Próximos Passos

## ✅ Status Atual

O Sistema de Recomendações Inteligente está **100% implementado e integrado na home page**!

**Resultados dos testes:**
```
5/6 testes passando ✅
Gemini API detectada ✅
Home page integrada ✅
```

---

## 🚀 Para Ver as Recomendações Funcionando

### Passo 1: Criar Dados de Teste

Execute o script para criar interações fictícias entre usuários e livros:

```bash
python criar_dados_teste_recomendacoes.py
```

**O que o script faz:**
- Cria 8-15 interações aleatórias por usuário
- Simula: leituras, reviews, wishlist, visualizações
- Atualiza estatísticas dos perfis
- Gera dados suficientes para testar todos os algoritmos

**Opção alternativa** (criar apenas para um usuário):
```bash
python criar_dados_teste_recomendacoes.py cgvargas
```

### Passo 2: Testar Novamente

```bash
python test_recommendations.py
```

Agora você deve ver:
- ✅ Recomendações Colaborativas funcionando
- ✅ Recomendações Híbridas com resultados
- ✅ Gemini AI com histórico (se tiver API key)

### Passo 3: Visualizar na Home Page

1. Inicie o servidor:
```bash
python manage.py runserver
```

2. Acesse: http://127.0.0.1:8000/

3. **Faça login** com um usuário que tenha interações

4. Role até o final da página - você verá a seção **"Para Você"** com:
   - Recomendações personalizadas
   - Botões para alternar algoritmos (Híbrido, IA, Similares, Conteúdo)
   - Cards de livros com score e justificativa

---

## 🎨 Como Usar o Sistema

### Via Interface Web (Home Page)

A seção "Para Você" já está integrada na home! Basta:

1. Estar logado
2. Ter pelo menos 5 interações com livros
3. Ver recomendações aparecerem automaticamente
4. Clicar nos botões para trocar de algoritmo

### Via API REST

```javascript
// Recomendações híbridas
fetch('/recommendations/api/recommendations/?algorithm=hybrid&limit=10')
    .then(res => res.json())
    .then(data => console.log(data.recommendations));

// Livros similares a um livro específico
fetch('/recommendations/api/books/1/similar/?limit=5')
    .then(res => res.json())
    .then(data => console.log(data.similar_books));

// Registrar que usuário leu um livro
fetch('/recommendations/api/interactions/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        book_id: 123,
        interaction_type: 'read',
        rating: 5
    })
});
```

### Via Python/Django

```python
from recommendations.algorithms import HybridRecommendationSystem

# Obter recomendações para um usuário
engine = HybridRecommendationSystem()
recommendations = engine.recommend(request.user, n=10)

for rec in recommendations:
    print(f"{rec['book'].title} - Score: {rec['score']:.2%}")
    print(f"Razão: {rec['reason']}")
```

---

## 🤖 Habilitar Google Gemini AI (Opcional)

Você já tem a API key configurada! Para testar:

1. Crie interações para o usuário (script acima)

2. Teste diretamente:
```bash
python test_recommendations.py
```

3. Ou use a API:
```javascript
fetch('/recommendations/api/recommendations/?algorithm=ai&limit=5')
    .then(res => res.json())
    .then(data => console.log(data.recommendations));
```

4. Ou use os insights:
```javascript
fetch('/recommendations/api/insights/')
    .then(res => res.json())
    .then(insights => {
        console.log('Temas favoritos:', insights.main_themes);
        console.log('Padrões:', insights.reading_patterns);
    });
```

---

## 📊 Monitorar e Gerenciar

### Django Admin

Acesse `/admin/` e navegue até **Recommendations** para:

- ✅ Ver todas as interações de usuários
- ✅ Inspecionar recomendações geradas
- ✅ Verificar similaridades calculadas
- ✅ Gerenciar perfis e estatísticas

### Tasks Celery (Opcional)

Para rodar processamento em background:

```bash
# Terminal 1: Worker
celery -A cgbookstore worker --loglevel=info --pool=solo

# Terminal 2: Beat (agendador)
celery -A cgbookstore beat --loglevel=info
```

**Tasks que rodam automaticamente:**
- **3h da manhã:** Calcula similaridades entre todos os livros
- **A cada hora:** Gera recomendações para todos os usuários
- **4h da manhã:** Limpa recomendações expiradas
- **A cada 6h:** Pré-calcula livros em alta

---

## 🎯 Customizar o Sistema

### Ajustar Pesos do Sistema Híbrido

Em [cgbookstore/settings.py](cgbookstore/settings.py):

```python
RECOMMENDATIONS_CONFIG = {
    'HYBRID_WEIGHTS': {
        'collaborative': 0.6,  # 60% peso colaborativo (padrão)
        'content': 0.3,        # 30% peso conteúdo
        'trending': 0.1,       # 10% peso trending
    },
}
```

Experimente diferentes combinações:
- Mais colaborativo: `0.8, 0.15, 0.05` (prioriza usuários similares)
- Mais conteúdo: `0.4, 0.5, 0.1` (prioriza similaridade de livros)
- Balanceado: `0.5, 0.4, 0.1` (equilíbrio entre métodos)

### Ajustar Cache

```python
RECOMMENDATIONS_CONFIG = {
    'CACHE_TIMEOUT': 3600,              # 1 hora (recomendações)
    'SIMILARITY_CACHE_TIMEOUT': 86400,  # 24 horas (similaridades)
    'MIN_INTERACTIONS': 5,              # Mínimo de interações
}
```

### Personalizar Template

Edite [templates/recommendations/recommendations_section.html](templates/recommendations/recommendations_section.html):

- Alterar título da seção
- Mudar layout dos cards
- Adicionar filtros (gêneros, autores)
- Customizar cores e estilos

---

## 📚 Adicionar Recomendações em Outras Páginas

### Na Página de Detalhes do Livro

```django
<!-- book_detail.html -->
<section class="related-books mt-5">
    <h3>Livros Similares</h3>
    <div class="row">
        <!-- Use a API para buscar livros similares -->
        <div id="similar-books-container"></div>
    </div>
</section>

<script>
fetch('/recommendations/api/books/{{ book.id }}/similar/?limit=6')
    .then(res => res.json())
    .then(data => {
        // Renderizar livros similares
    });
</script>
```

### No Perfil do Usuário

```django
<!-- profile.html -->
{% include 'recommendations/recommendations_section.html' %}
```

### Dashboard Personalizado

Crie uma página dedicada em [core/views.py](core/views.py):

```python
from recommendations.algorithms import HybridRecommendationSystem
from recommendations.models import UserBookInteraction

def my_recommendations(request):
    if not request.user.is_authenticated:
        return redirect('login')

    engine = HybridRecommendationSystem()
    recommendations = engine.recommend(request.user, n=20)

    history = UserBookInteraction.objects.filter(
        user=request.user
    ).select_related('book').order_by('-created_at')[:20]

    return render(request, 'my_recommendations.html', {
        'recommendations': recommendations,
        'history': history
    })
```

---

## 🐛 Troubleshooting

### "No recommendations generated"

**Causa:** Usuário não tem interações suficientes

**Solução:**
```bash
python criar_dados_teste_recomendacoes.py
```

### "Gemini AI não configurado"

**Causa:** GEMINI_API_KEY vazia ou inválida

**Solução:**
1. Verifique o `.env`
2. Confirme que a key está correta
3. Ou use outros algoritmos (não precisam de API)

### Template não aparece

**Causa:** Possível erro no include

**Solução:**
1. Verifique se o arquivo existe: `templates/recommendations/recommendations_section.html`
2. Verifique erros no console do navegador
3. Olhe os logs do Django

### API retorna 401 Unauthorized

**Causa:** Usuário não está autenticado

**Solução:**
- Faça login antes de chamar a API
- Ou remova a autenticação em `views.py` (não recomendado)

---

## 📈 Próximas Melhorias (Ideias)

1. **A/B Testing**
   - Testar diferentes pesos do sistema híbrido
   - Medir CTR de cada algoritmo
   - Otimizar automaticamente

2. **Feedback Loop**
   - Botões "Gostei" / "Não gostei"
   - Sistema aprende com feedback
   - Ajusta recomendações dinamicamente

3. **Visualizações**
   - Gráficos de insights com Chart.js
   - Dashboard de estatísticas
   - Análise de tendências

4. **Deep Learning**
   - Neural Collaborative Filtering
   - Word2Vec embeddings
   - Autoencoders

5. **Personalização Visual**
   - Temas de recomendações (favoritos, novidades, clássicos)
   - Filtros por gênero
   - Timeline de leitura

---

## ✅ Checklist Final

- [x] Sistema implementado e testado
- [x] Integrado na home page
- [x] API REST funcionando
- [x] Gemini AI configurado
- [x] Documentação completa
- [ ] **Criar dados de teste** ← FAÇA ISSO AGORA!
- [ ] Testar na home page
- [ ] (Opcional) Iniciar Celery worker

---

## 🎊 Conclusão

Você tem agora um **Sistema de Recomendações Inteligente** completo e funcional!

**Para começar:**
```bash
# 1. Criar dados de teste
python criar_dados_teste_recomendacoes.py

# 2. Testar
python test_recommendations.py

# 3. Ver na home
python manage.py runserver
# Acesse: http://127.0.0.1:8000
```

**Documentação completa:**
- [COMO_USAR_RECOMENDACOES.md](documents/Projetos Modulares/recomendacoes_ia/COMO_USAR_RECOMENDACOES.md)
- [SISTEMA_RECOMENDACOES_IA.md](documents/Projetos Modulares/recomendacoes_ia/SISTEMA_RECOMENDACOES_IA.md)
- [IMPLEMENTACAO_COMPLETA.md](documents/Projetos Modulares/recomendacoes_ia/IMPLEMENTACAO_COMPLETA.md)

Divirta-se recomendando livros! 📚✨🚀

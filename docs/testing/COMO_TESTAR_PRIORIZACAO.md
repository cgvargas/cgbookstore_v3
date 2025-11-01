# 🧪 Como Testar o Sistema de Priorização

## Método 1: Shell Interativo (Recomendado)

```bash
python manage.py shell
```

Depois, cole este código linha por linha:

```python
# 1. Importar
from django.contrib.auth.models import User
from recommendations.preference_analyzer import UserPreferenceAnalyzer, ShelfWeightConfig
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

# 2. Pegar usuário
user = User.objects.first()
print(f"Testando com: {user.username}")

# 3. Analisar preferências
analyzer = UserPreferenceAnalyzer(user)
profile = analyzer.get_preference_profile()

print(f"\n📊 PERFIL DO USUÁRIO:")
print(f"Total de livros: {profile['total_books']}")
print(f"Top gênero: {profile['top_genres'][0]['genre'] if profile['top_genres'] else 'N/A'}")
print(f"Top autor: {profile['top_authors'][0]['author'] if profile['top_authors'] else 'N/A'}")

# 4. Testar algoritmo
engine = PreferenceWeightedHybrid()
recs = engine.recommend(user, n=6)

print(f"\n🎯 RECOMENDAÇÕES GERADAS: {len(recs)}")
for i, rec in enumerate(recs[:3], 1):
    print(f"{i}. {rec['book'].title} - Score: {rec['score']:.2f}")
    if 'preference_boost' in rec:
        print(f"   BOOST: +{rec['preference_boost']*100:.0f}%")

print("\n✅ SUCESSO!")
```

## Método 2: Script Automático

```bash
python manage.py shell
```

```python
exec(open('quick_test_preferences.py').read())
```

## Método 3: Teste Completo (Relatório Detalhado)

```python
from recommendations.preference_analyzer import print_user_preference_report
from django.contrib.auth.models import User

user = User.objects.first()
print_user_preference_report(user)
```

## Método 4: Comparação Antes vs Depois

```python
from recommendations.algorithms import HybridRecommendationSystem
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid
from django.contrib.auth.models import User

user = User.objects.first()

# ANTES (sem priorização)
normal_engine = HybridRecommendationSystem()
normal_recs = normal_engine.recommend(user, n=6)

print("📊 ALGORITMO NORMAL:")
for i, rec in enumerate(normal_recs, 1):
    print(f"{i}. {rec['book'].title[:40]} - Score: {rec['score']:.2f}")

# DEPOIS (com priorização)
pref_engine = PreferenceWeightedHybrid()
pref_recs = pref_engine.recommend(user, n=6)

print("\n🎯 ALGORITMO PONDERADO:")
for i, rec in enumerate(pref_recs, 1):
    boost = f" (BOOST: +{rec.get('preference_boost', 0)*100:.0f}%)" if 'preference_boost' in rec else ""
    print(f"{i}. {rec['book'].title[:40]} - Score: {rec['score']:.2f}{boost}")
```

## Verificar Pesos Configurados

```python
from recommendations.preference_analyzer import ShelfWeightConfig

print("📊 CONFIGURAÇÃO DE PESOS:")
for shelf_type in ['favorites', 'read', 'reading', 'to_read', 'abandoned']:
    weight = ShelfWeightConfig.get_weight(shelf_type)
    desc = ShelfWeightConfig.get_description(shelf_type)
    print(f"{desc}: {weight:.0%}")
```

## Analisar Livro Específico

```python
from recommendations.preference_analyzer import UserPreferenceAnalyzer
from core.models import Book
from django.contrib.auth.models import User

user = User.objects.first()
analyzer = UserPreferenceAnalyzer(user)

# Pegar um livro qualquer
book = Book.objects.first()

# Pontuar baseado nas preferências do usuário
score = analyzer.score_book_by_preference(book)
print(f"Livro: {book.title}")
print(f"Score de relevância: {score:.2f} (0-1)")
print(f"Estrelas: {'⭐' * int(score * 5)}")
```

## Troubleshooting

### Erro: "No module named 'recommendations.preference_analyzer'"

```python
# Verificar se módulo existe
import os
path = "recommendations/preference_analyzer.py"
print(f"Arquivo existe: {os.path.exists(path)}")
```

### Erro: "User has no books"

```python
# Verificar livros do usuário
from django.contrib.auth.models import User

user = User.objects.first()
book_count = user.bookshelves.count()
print(f"Livros nas prateleiras: {book_count}")

if book_count == 0:
    print("⚠ Usuário não tem livros. Teste com outro usuário:")
    users_with_books = User.objects.annotate(
        num_books=Count('bookshelves')
    ).filter(num_books__gt=0)

    for u in users_with_books[:5]:
        print(f"  - {u.username}: {u.bookshelves.count()} livros")
```

### Verificar Sintaxe

```bash
# Fora do shell Django
python -m py_compile recommendations/preference_analyzer.py
python -m py_compile recommendations/algorithms_preference_weighted.py
```

## Próximos Passos Após Teste Bem-Sucedido

1. **Integrar em Produção**
   ```python
   # Em recommendations/views_simple.py
   # Substituir:
   from recommendations.algorithms import HybridRecommendationSystem
   # Por:
   from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid
   ```

2. **Monitorar Performance**
   - Verificar logs de tempo de execução
   - Comparar scores antes vs depois
   - Coletar feedback dos usuários

3. **A/B Testing**
   - 50% usuários veem algoritmo ponderado
   - 50% usuários veem algoritmo normal
   - Comparar CTR e conversão

## Referências

- **Documentação Completa:** `documents/SISTEMA_PRIORIZACAO_PRATELEIRAS.md`
- **Status do Projeto:** `documents/status/status_01112025.md`
- **Código Fonte:**
  - `recommendations/preference_analyzer.py`
  - `recommendations/algorithms_preference_weighted.py`

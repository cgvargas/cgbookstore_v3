# 🤖 SISTEMA DE RECOMENDAÇÕES INTELIGENTE COM IA

**Projeto:** CGBookStore v3
**Data:** 27/10/2025
**Versão:** 1.0
**Status:** Pronto para implementação
**Pré-requisito:** ✅ Otimizações de escalabilidade concluídas

---

## 📋 ÍNDICE

1. [Visão Geral](#visao-geral)
2. [Arquitetura do Sistema](#arquitetura)
3. [Algoritmos de Recomendação](#algoritmos)
4. [Modelos de Dados](#modelos)
5. [Implementação](#implementacao)
6. [APIs e Endpoints](#apis)
7. [Performance e Cache](#performance)
8. [Testes](#testes)
9. [Deploy](#deploy)

---

## 🎯 VISÃO GERAL {#visao-geral}

### O que é?

Um sistema inteligente de recomendações de livros que utiliza:
- **Filtragem Colaborativa** - "Quem leu X também leu Y"
- **Baseado em Conteúdo** - Similaridade entre livros (gênero, autor, tags)
- **Sistema Híbrido** - Combinação dos dois métodos
- **IA Premium (opcional)** - OpenAI GPT para recomendações personalizadas

### Objetivos:

✅ Aumentar engajamento dos usuários
✅ Aumentar tempo de permanência no site
✅ Aumentar número de livros lidos
✅ Melhorar experiência do usuário
✅ Coletar dados para análises futuras

### Métricas de Sucesso:

- **Engajamento:** +40% de cliques em recomendações
- **Retenção:** +30% de usuários retornando
- **Conversão:** +25% de livros adicionados à leitura
- **Satisfação:** 4.5+ estrelas de avaliação

---

## 🏗️ ARQUITETURA DO SISTEMA {#arquitetura}

### Componentes Principais:

```
┌─────────────────────────────────────────────────┐
│           CAMADA DE APRESENTAÇÃO                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Views   │  │Templates │  │   APIs   │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         CAMADA DE LÓGICA DE NEGÓCIO             │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Algoritmos  │  │   Scoring    │           │
│  │Recomendação  │  │  Híbrido     │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│          CAMADA DE PROCESSAMENTO                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Celery  │  │  Cache   │  │   ML     │     │
│  │  Tasks   │  │  Redis   │  │  Models  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│            CAMADA DE DADOS                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │PostgreSQL│  │  Models  │  │  APIs    │     │
│  │ Supabase │  │  Django  │  │Externas  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────┘
```

### Fluxo de Dados:

1. **Coleta de Dados**
   - Usuário visualiza livro → Registrar
   - Usuário lê livro → Registrar
   - Usuário avalia livro → Registrar
   - Usuário adiciona à lista → Registrar

2. **Processamento (Celery)**
   - Atualizar perfil do usuário
   - Recalcular similaridades
   - Atualizar matriz de recomendações
   - Cachear resultados

3. **Geração de Recomendações**
   - Aplicar algoritmo colaborativo
   - Aplicar algoritmo de conteúdo
   - Combinar scores (híbrido)
   - Aplicar filtros e regras

4. **Entrega**
   - Buscar em cache (Redis)
   - Se não existe, calcular
   - Retornar top N recomendações
   - Registrar clique/interação

---

## 🧮 ALGORITMOS DE RECOMENDAÇÃO {#algoritmos}

### 1. Filtragem Colaborativa (Collaborative Filtering)

**Conceito:** "Usuários similares gostam de livros similares"

**Implementação:**
- User-Based: Encontrar usuários similares e recomendar o que eles leram
- Item-Based: Encontrar livros similares aos que o usuário gostou

**Fórmula (Similaridade de Cosseno):**
```python
similarity = dot(user_A_vector, user_B_vector) / (norm(user_A) * norm(user_B))
```

**Prós:**
- Descobre padrões não óbvios
- Funciona sem informações do conteúdo
- Melhora com mais dados

**Contras:**
- Cold start (novos usuários/livros)
- Precisa de muitos dados
- Computacionalmente caro

### 2. Baseado em Conteúdo (Content-Based)

**Conceito:** "Se você gostou de X, vai gostar de Y (similar)"

**Implementação:**
- Analisar características dos livros (gênero, autor, tags, descrição)
- Criar perfil do usuário baseado em preferências
- Recomendar livros com características similares

**Fórmula (Similaridade TF-IDF):**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(books_descriptions)
similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
```

**Prós:**
- Não precisa de dados de outros usuários
- Funciona para novos livros
- Transparente (explicável)

**Contras:**
- Não descobre novas preferências
- Limitado aos dados de conteúdo
- Recomendações previsíveis

### 3. Sistema Híbrido

**Conceito:** Combinar ambos os métodos

**Implementação:**
```python
score_final = (
    peso_colaborativo * score_colaborativo +
    peso_conteudo * score_conteudo +
    bonus_popularidade +
    bonus_recente
)
```

**Pesos Sugeridos:**
- Colaborativo: 60%
- Conteúdo: 30%
- Popularidade: 5%
- Recente: 5%

**Prós:**
- Combina vantagens de ambos
- Mais robusto
- Melhor performance

**Contras:**
- Mais complexo
- Mais difícil de debugar

### 4. IA Premium (Google Gemini) ✨

**Conceito:** Usar Google Gemini para análise de texto e recomendações contextuais

**Implementação:**
```python
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

prompt = f"""
Você é um assistente especializado em recomendações de livros.

Perfil do usuário:
- Gêneros preferidos: {user_profile.preferred_genres}
- Autores favoritos: {user_profile.preferred_authors}
- Livros lidos recentemente: {recent_books}
- Avaliações médias: {user_profile.avg_rating}

Baseado nesse perfil, recomende 5 livros em português e explique:
1. Por que cada livro é adequado para este usuário
2. Qual a conexão com os livros que ele já leu
3. O que ele vai gostar em cada livro

Formato: JSON com {{"livro": "...", "autor": "...", "motivo": "..."}}
"""

response = model.generate_content(prompt)
recommendations = json.loads(response.text)
```

**Vantagens do Gemini:**
- ✅ **Gratuito** ou muito mais barato que OpenAI
- ✅ **Contexto gigante** (2M tokens vs 128K do GPT-4)
- ✅ **Multimodal** (pode analisar capas de livros)
- ✅ **Português nativo** (entende muito bem PT-BR)
- ✅ **Rápido** (latência baixa)
- ✅ **JSON mode** nativo

**Casos de uso:**
- Recomendações com explicações personalizadas
- Análise de sinopses e reviews
- Criar descrições de "Por que você vai gostar"
- Resumos inteligentes de livros
- Matchmaking leitor-livro

---

## 📊 MODELOS DE DADOS {#modelos}

### 1. UserProfile (Perfil do Usuário)

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Preferências inferidas
    preferred_genres = models.JSONField(default=list)  # ['fiction', 'sci-fi']
    preferred_authors = models.JSONField(default=list)
    preferred_tags = models.JSONField(default=list)

    # Estatísticas
    books_read_count = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    favorite_genre = models.CharField(max_length=100, blank=True)

    # Vector de preferências (para colaborativa)
    preference_vector = models.JSONField(default=dict)

    # Metadados
    last_recommendation_at = models.DateTimeField(null=True, blank=True)
    recommendations_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 2. Recommendation (Recomendação)

```python
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # Scores
    collaborative_score = models.FloatField(default=0.0)
    content_score = models.FloatField(default=0.0)
    hybrid_score = models.FloatField(default=0.0)

    # Ranking
    rank = models.IntegerField()  # 1, 2, 3...

    # Explicação
    reason = models.TextField(blank=True)  # "Porque você leu X"
    algorithm = models.CharField(max_length=50)  # 'collaborative', 'content', 'hybrid'

    # Feedback
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    converted = models.BooleanField(default=False)  # Adicionou à leitura

    # Metadados
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Cache por 24h

    class Meta:
        unique_together = ['user', 'book', 'generated_at']
        indexes = [
            models.Index(fields=['user', '-hybrid_score']),
            models.Index(fields=['user', '-generated_at']),
        ]
```

### 3. UserBookInteraction (Interação)

```python
class UserBookInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'Visualizou'),
        ('read', 'Leu'),
        ('rate', 'Avaliou'),
        ('favorite', 'Favoritou'),
        ('share', 'Compartilhou'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)

    # Dados adicionais
    rating = models.IntegerField(null=True, blank=True)  # 1-5
    duration_seconds = models.IntegerField(null=True)  # Tempo de leitura

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['book', 'interaction_type']),
            models.Index(fields=['-created_at']),
        ]
```

### 4. BookSimilarity (Similaridade entre Livros)

```python
class BookSimilarity(models.Model):
    book_a = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='similar_to')
    book_b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='similar_from')

    # Scores de similaridade
    content_similarity = models.FloatField()  # 0.0 - 1.0
    collaborative_similarity = models.FloatField(default=0.0)

    # Metadados
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['book_a', 'book_b']
        indexes = [
            models.Index(fields=['book_a', '-content_similarity']),
        ]
```

---

## 🛠️ IMPLEMENTAÇÃO {#implementacao}

### Fase 1: Setup Inicial

**Arquivos a criar:**
```
recommendations/
├── __init__.py
├── models.py           # Modelos acima
├── algorithms/
│   ├── __init__.py
│   ├── collaborative.py
│   ├── content_based.py
│   └── hybrid.py
├── services/
│   ├── __init__.py
│   ├── profile_builder.py
│   ├── similarity_calculator.py
│   └── recommendation_engine.py
├── tasks.py            # Celery tasks
├── views.py            # Views
├── serializers.py      # DRF serializers
└── urls.py             # URLs
```

### Fase 2: Algoritmo Colaborativo

```python
# recommendations/algorithms/collaborative.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache

class CollaborativeFilter:
    def __init__(self):
        self.user_item_matrix = None

    def build_matrix(self):
        """Constrói matriz usuário-item."""
        # Buscar todas as interações
        interactions = UserBookInteraction.objects.filter(
            interaction_type__in=['read', 'rate']
        ).values('user_id', 'book_id', 'rating')

        # Criar matriz esparsa
        # ... código de construção

    def find_similar_users(self, user_id, top_n=10):
        """Encontra usuários similares."""
        user_vector = self.get_user_vector(user_id)

        # Calcular similaridade
        similarities = cosine_similarity([user_vector], self.user_item_matrix)

        # Retornar top N
        return np.argsort(similarities[0])[-top_n:]

    def recommend(self, user_id, n=10):
        """Gera recomendações colaborativas."""
        similar_users = self.find_similar_users(user_id)

        # Livros que usuários similares leram
        books = Book.objects.filter(
            userbookinteraction__user_id__in=similar_users,
            userbookinteraction__interaction_type='read'
        ).exclude(
            userbookinteraction__user_id=user_id
        ).annotate(
            score=Count('id')
        ).order_by('-score')[:n]

        return books
```

### Fase 3: Algoritmo Baseado em Conteúdo

```python
# recommendations/algorithms/content_based.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedFilter:
    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=500)
        self.book_vectors = None

    def build_vectors(self):
        """Cria vetores TF-IDF para todos os livros."""
        books = Book.objects.all()

        # Combinar características
        texts = []
        for book in books:
            text = f"{book.title} {book.description} {book.genres} {book.author}"
            texts.append(text)

        # Vetorizar
        self.book_vectors = self.tfidf.fit_transform(texts)

        # Cachear
        cache.set('book_vectors', self.book_vectors, timeout=86400)  # 24h

    def find_similar_books(self, book_id, top_n=10):
        """Encontra livros similares."""
        book = Book.objects.get(id=book_id)
        book_index = list(Book.objects.values_list('id', flat=True)).index(book_id)

        # Calcular similaridade
        similarities = cosine_similarity(
            self.book_vectors[book_index],
            self.book_vectors
        )

        # Retornar top N (excluindo o próprio livro)
        similar_indices = np.argsort(similarities[0])[-top_n-1:-1]
        similar_book_ids = [list(Book.objects.values_list('id', flat=True))[i]
                           for i in similar_indices]

        return Book.objects.filter(id__in=similar_book_ids)

    def recommend(self, user_id, n=10):
        """Gera recomendações baseadas em conteúdo."""
        # Livros que o usuário gostou (rating >= 4)
        liked_books = UserBookInteraction.objects.filter(
            user_id=user_id,
            interaction_type='rate',
            rating__gte=4
        ).values_list('book_id', flat=True)

        # Encontrar similares
        recommendations = []
        for book_id in liked_books:
            similar = self.find_similar_books(book_id, top_n=5)
            recommendations.extend(similar)

        # Remover duplicatas e livros já lidos
        unique_recs = list(set(recommendations))

        return unique_recs[:n]
```

### Fase 4: Sistema Híbrido

```python
# recommendations/algorithms/hybrid.py

class HybridRecommender:
    def __init__(self):
        self.collaborative = CollaborativeFilter()
        self.content_based = ContentBasedFilter()

    def recommend(self, user_id, n=10):
        """Combina ambos os métodos."""
        # Pesos
        w_collab = 0.6
        w_content = 0.3
        w_popularity = 0.05
        w_recent = 0.05

        # Obter recomendações de cada método
        collab_recs = self.collaborative.recommend(user_id, n=20)
        content_recs = self.content_based.recommend(user_id, n=20)

        # Combinar scores
        scores = {}

        for book in collab_recs:
            scores[book.id] = scores.get(book.id, 0) + w_collab

        for book in content_recs:
            scores[book.id] = scores.get(book.id, 0) + w_content

        # Adicionar bônus de popularidade
        popular_books = Book.objects.annotate(
            reads_count=Count('userbookinteraction')
        ).order_by('-reads_count')[:50]

        for book in popular_books:
            if book.id in scores:
                scores[book.id] += w_popularity

        # Adicionar bônus de recentes
        recent_books = Book.objects.order_by('-created_at')[:50]

        for book in recent_books:
            if book.id in scores:
                scores[book.id] += w_recent

        # Ordenar por score
        sorted_books = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        book_ids = [book_id for book_id, score in sorted_books[:n]]

        return Book.objects.filter(id__in=book_ids)
```

---

## 🚀 APIS E ENDPOINTS {#apis}

### Endpoints REST

```python
# recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Recomendações para usuário
    path('for-you/', views.recommendations_for_user, name='for_you'),

    # Livros similares
    path('similar/<int:book_id>/', views.similar_books, name='similar'),

    # Registrar interação
    path('interact/', views.register_interaction, name='interact'),

    # Atualizar perfil
    path('profile/update/', views.update_profile, name='update_profile'),
]
```

### Views

```python
# recommendations/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

@api_view(['GET'])
def recommendations_for_user(request):
    """Retorna recomendações personalizadas."""
    user = request.user

    # Buscar em cache
    cache_key = f'recommendations:user:{user.id}'
    cached = cache.get(cache_key)

    if cached:
        return Response(cached)

    # Gerar recomendações
    recommender = HybridRecommender()
    books = recommender.recommend(user.id, n=10)

    # Serializar
    data = RecommendationSerializer(books, many=True).data

    # Cachear por 1 hora
    cache.set(cache_key, data, timeout=3600)

    return Response(data)

@api_view(['GET'])
def similar_books(request, book_id):
    """Retorna livros similares."""
    cache_key = f'similar:book:{book_id}'
    cached = cache.get(cache_key)

    if cached:
        return Response(cached)

    content_filter = ContentBasedFilter()
    similar = content_filter.find_similar_books(book_id, top_n=10)

    data = BookSerializer(similar, many=True).data
    cache.set(cache_key, data, timeout=86400)  # 24h

    return Response(data)

@api_view(['POST'])
def register_interaction(request):
    """Registra interação do usuário."""
    user = request.user
    book_id = request.data.get('book_id')
    interaction_type = request.data.get('type')
    rating = request.data.get('rating')

    # Criar interação
    interaction = UserBookInteraction.objects.create(
        user=user,
        book_id=book_id,
        interaction_type=interaction_type,
        rating=rating
    )

    # Invalidar cache
    cache.delete(f'recommendations:user:{user.id}')

    # Atualizar perfil (assíncrono)
    from .tasks import update_user_profile
    update_user_profile.delay(user.id)

    return Response({'status': 'ok'})
```

---

## ⚡ PERFORMANCE E CACHE {#performance}

### Estratégias de Cache

```python
# 1. Cache de recomendações por usuário (1 hora)
cache_key = f'recommendations:user:{user_id}'
cache.set(cache_key, recommendations, timeout=3600)

# 2. Cache de similaridade entre livros (24 horas)
cache_key = f'similar:book:{book_id}'
cache.set(cache_key, similar_books, timeout=86400)

# 3. Cache de matriz de colaborativa (6 horas)
cache_key = 'collaborative:matrix'
cache.set(cache_key, user_item_matrix, timeout=21600)

# 4. Cache de vetores TF-IDF (24 horas)
cache_key = 'content:vectors'
cache.set(cache_key, tfidf_vectors, timeout=86400)
```

### Tasks Celery

```python
# recommendations/tasks.py

from celery import shared_task

@shared_task
def update_user_profile(user_id):
    """Atualiza perfil do usuário."""
    profile, _ = UserProfile.objects.get_or_create(user_id=user_id)

    # Calcular preferências
    interactions = UserBookInteraction.objects.filter(
        user_id=user_id,
        interaction_type__in=['read', 'rate']
    )

    # Atualizar gêneros preferidos
    genres = []
    for interaction in interactions:
        genres.extend(interaction.book.genres)

    profile.preferred_genres = list(set(genres))
    profile.books_read_count = interactions.count()
    profile.save()

    # Invalidar cache
    cache.delete(f'recommendations:user:{user_id}')

@shared_task
def recalculate_similarities():
    """Recalcula similaridades entre livros (rodar diariamente)."""
    content_filter = ContentBasedFilter()
    content_filter.build_vectors()

    # Calcular e salvar similaridades
    books = Book.objects.all()

    for book in books:
        similar = content_filter.find_similar_books(book.id, top_n=20)

        for similar_book in similar:
            BookSimilarity.objects.update_or_create(
                book_a=book,
                book_b=similar_book,
                defaults={'content_similarity': 0.8}  # Calcular real
            )

@shared_task
def generate_recommendations_batch():
    """Gera recomendações para todos os usuários ativos (rodar à noite)."""
    users = User.objects.filter(is_active=True)
    recommender = HybridRecommender()

    for user in users:
        books = recommender.recommend(user.id, n=10)

        # Salvar no banco
        for rank, book in enumerate(books, 1):
            Recommendation.objects.create(
                user=user,
                book=book,
                rank=rank,
                hybrid_score=1.0,  # Calcular real
                expires_at=timezone.now() + timedelta(days=1)
            )
```

---

## 🧪 TESTES {#testes}

### Testes Unitários

```python
# recommendations/tests.py

from django.test import TestCase

class CollaborativeFilterTests(TestCase):
    def test_find_similar_users(self):
        # Setup
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        book = Book.objects.create(title='Test Book')

        # Both users read same book
        UserBookInteraction.objects.create(
            user=user1, book=book, interaction_type='read'
        )
        UserBookInteraction.objects.create(
            user=user2, book=book, interaction_type='read'
        )

        # Test
        cf = CollaborativeFilter()
        similar = cf.find_similar_users(user1.id)

        self.assertIn(user2.id, similar)
```

---

## 📦 DEPLOY {#deploy}

### Celery Beat Schedule

```python
# cgbookstore/celery.py

app.conf.beat_schedule = {
    # ... outras tasks

    # Recalcular similaridades (todo dia às 3h)
    'recalculate-similarities': {
        'task': 'recommendations.tasks.recalculate_similarities',
        'schedule': crontab(hour=3, minute=0),
    },

    # Gerar recomendações batch (todo dia às 4h)
    'generate-recommendations': {
        'task': 'recommendations.tasks.generate_recommendations_batch',
        'schedule': crontab(hour=4, minute=0),
    },
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Criar app `recommendations`
- [ ] Criar modelos de dados
- [ ] Fazer migrations
- [ ] Implementar algoritmo colaborativo
- [ ] Implementar algoritmo de conteúdo
- [ ] Implementar sistema híbrido
- [ ] Criar views e endpoints
- [ ] Criar serializers
- [ ] Adicionar URLs
- [ ] Implementar cache
- [ ] Criar tasks Celery
- [ ] Adicionar ao Beat schedule
- [ ] Criar testes
- [ ] Documentar APIs
- [ ] Deploy

---

**FIM DA DOCUMENTAÇÃO**

**Próximo passo:** Autorizar implementação!

Comando sugerido:
```
Claude, você está AUTORIZADO a implementar o Sistema de Recomendações Inteligente conforme documentado. Comece criando o app recommendations e os modelos.
```

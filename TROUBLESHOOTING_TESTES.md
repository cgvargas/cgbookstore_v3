# 🔧 Troubleshooting - Testes do Sistema de Priorização

## Problemas Comuns e Soluções

### 1. TypeError: sequence item 0: expected str instance, Category found

**Sintoma:**
```
TypeError: sequence item 0: expected str instance, Category found
```

**Causa:**
Código antigo ainda carregado no shell Django.

**Solução:**

#### Opção A: Reiniciar Shell (Recomendado)
```python
exit()  # Sair do shell
```

Depois:
```bash
python manage.py shell
```

```python
# Importar novamente
from django.contrib.auth.models import User
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

user = User.objects.first()
engine = PreferenceWeightedHybrid()
recs = engine.recommend(user, n=6)
```

#### Opção B: Reload do Módulo
```python
import importlib
import recommendations.algorithms_preference_weighted
importlib.reload(recommendations.algorithms_preference_weighted)

from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

# Testar novamente
user = User.objects.first()
engine = PreferenceWeightedHybrid()
recs = engine.recommend(user, n=6)
```

---

### 2. UnicodeDecodeError ao executar script

**Sintoma:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81
```

**Solução:**
Usar encoding UTF-8:

```python
# ERRADO:
exec(open('quick_test_preferences.py').read())

# CORRETO:
exec(open('test_preferences_basic.py', encoding='utf-8').read())
```

Ou usar o script sem caracteres especiais:
```python
exec(open('test_preferences_basic.py', encoding='utf-8').read())
```

---

### 3. No similar users found for [username]

**Sintoma:**
```
No similar users found for claud, using popular books
```

**É Normal?**
✅ **SIM!** Isso não é um erro.

**Explicação:**
O algoritmo colaborativo não encontrou outros usuários com livros suficientes em comum. Neste caso, ele automaticamente usa livros populares como fallback.

**Isso não afeta o funcionamento:**
- O algoritmo content-based ainda funciona (baseado nos livros do usuário)
- O sistema híbrido combina os resultados
- As recomendações continuam sendo geradas normalmente

**Como ter usuários similares:**
- Adicione mais usuários ao sistema
- Adicione mais livros às prateleiras dos usuários
- Com mais dados, o algoritmo colaborativo encontrará padrões

---

### 4. NameError: name 'recs' is not defined

**Sintoma:**
```python
print(f"\nRecomendacoes: {len(recs)}")
NameError: name 'recs' is not defined
```

**Causa:**
A linha anterior deu erro e `recs` não foi criado.

**Solução:**
Corrija o erro anterior primeiro, depois execute novamente:

```python
# Certifique-se que esta linha funciona:
recs = engine.recommend(user, n=6)

# Só então:
print(f"\nRecomendacoes: {len(recs)}")
```

---

### 5. ImportError: No module named 'recommendations.preference_analyzer'

**Sintoma:**
```
ImportError: No module named 'recommendations.preference_analyzer'
```

**Solução:**

1. Verificar se arquivo existe:
```python
import os
print(os.path.exists('recommendations/preference_analyzer.py'))
# Deve retornar: True
```

2. Se não existir, houve problema no git:
```bash
git status
git pull
```

3. Verificar PYTHONPATH:
```python
import sys
print('\n'.join(sys.path))
```

---

### 6. AttributeError: 'Book' object has no attribute 'has_valid_cover'

**Sintoma:**
```
AttributeError: 'Book' object has no attribute 'has_valid_cover'
```

**Causa:**
Mudança no modelo Book não foi aplicada.

**Solução:**

1. Verificar se propriedade existe:
```bash
grep -n "has_valid_cover" core/models/book.py
```

2. Se não existir, adicionar ao modelo:
```python
# core/models/book.py

@property
def has_valid_cover(self):
    """Verifica se o livro possui uma capa válida."""
    return bool(self.cover_image and self.cover_image.name)
```

3. Reiniciar shell

---

### 7. User has no books (sem livros nas prateleiras)

**Sintoma:**
```
Total de livros: 0
```

**Solução:**

Encontrar usuário com livros:
```python
from django.contrib.auth.models import User
from django.db.models import Count

users_with_books = User.objects.annotate(
    book_count=Count('bookshelves')
).filter(book_count__gt=0).order_by('-book_count')

for u in users_with_books[:5]:
    print(f"{u.username}: {u.bookshelves.count()} livros")

# Usar usuário com mais livros
user = users_with_books.first()
```

Ou adicionar livros para o usuário atual:
```python
from accounts.models import BookShelf
from core.models import Book

# Adicionar alguns livros como favoritos
books = Book.objects.all()[:5]
for book in books:
    BookShelf.objects.create(
        user=user,
        book=book,
        shelf_type='favorites'
    )
```

---

## ✅ Checklist de Validação

Antes de reportar um problema, verifique:

- [ ] Shell Django foi reiniciado após mudanças no código
- [ ] Encoding UTF-8 está sendo usado nos scripts
- [ ] Usuário tem livros nas prateleiras
- [ ] Arquivos do sistema existem (preference_analyzer.py, etc)
- [ ] Modelo Book tem propriedade `has_valid_cover`
- [ ] Git pull foi executado (código atualizado)

---

## 🆘 Comandos de Diagnóstico

```python
# Verificar importações
from django.contrib.auth.models import User
from recommendations.preference_analyzer import UserPreferenceAnalyzer
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid
print("Importacoes OK!")

# Verificar usuario
user = User.objects.first()
print(f"Usuario: {user.username}")
print(f"Livros: {user.bookshelves.count()}")

# Verificar modelo Book
from core.models import Book
book = Book.objects.first()
print(f"has_valid_cover: {hasattr(book, 'has_valid_cover')}")

# Verificar sintaxe dos arquivos
import py_compile
py_compile.compile('recommendations/preference_analyzer.py')
py_compile.compile('recommendations/algorithms_preference_weighted.py')
print("Sintaxe OK!")
```

---

## 📞 Se Nada Funcionar

1. **Limpar cache do Python:**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

2. **Reinstalar dependências:**
```bash
pip install -r requirements.txt --force-reinstall
```

3. **Verificar commits:**
```bash
git log --oneline -10 | grep -i priori
```

4. **Voltar para versão anterior:**
```bash
git checkout 028dcf3  # Último commit funcional
```

---

## 💡 Dicas

- Sempre reinicie o shell após mudanças no código
- Use `test_preferences_basic.py` para evitar problemas de encoding
- Teste com usuário que tenha pelo menos 5 livros nas prateleiras
- A mensagem "No similar users" é normal em sistemas com poucos usuários

---

**Última atualização:** 01/11/2025
**Versão do sistema:** 1.0

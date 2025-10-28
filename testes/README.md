# 🧪 Testes - Scripts de Teste e Diagnóstico

Esta pasta contém todos os scripts de teste, diagnóstico e utilitários do projeto.

## 📋 Categorias de Arquivos

### 🤖 Testes de Recomendações com IA

1. **test_enhanced_ai.py**
   - Teste completo do sistema potencializado (IA + Google Books)
   - Verifica exclusão de livros conhecidos
   - Performance: ~6-8 segundos (primeira vez)

2. **test_ai_recommendations.py**
   - Teste do algoritmo IA Premium (Gemini)
   - Valida resposta JSON e estrutura

3. **test_recommendations.py**
   - Testes gerais do sistema de recomendações
   - Algoritmos: Híbrido, Colaborativo, Conteúdo

### 🔌 Testes de API

4. **test_api_recommendations.py**
   - Teste do endpoint `/recommendations/api/recommendations/`
   - Validação de autenticação e permissões

5. **test_user_claud.py**
   - Teste específico para o usuário 'claud'
   - Verifica interações e prateleiras

### 🧠 Testes de Modelos IA

6. **test_gemini_model.py**
   - Lista modelos disponíveis do Gemini
   - Testa conectividade com API
   - Valida modelo `gemini-2.5-flash`

### 💾 Testes de Cache e Performance

7. **test_cache_quick.py**
   - Testes rápidos de cache
   - Valida Redis/Database session

8. **test_performance.py**
   - Testes de performance do sistema
   - Benchmarks de algoritmos

9. **test_performance_simple.py**
   - Versão simplificada de testes de performance

### 🗄️ Testes de Banco de Dados

10. **test_db.py**
    - Testes de conexão com banco
    - Validação de modelos

11. **test_notifications.py**
    - Testes do sistema de notificações

### 🛠️ Scripts Utilitários

12. **criar_dados_teste_recomendacoes.py**
    - Popula banco com dados de teste para recomendações
    - Cria interações fictícias de usuários

13. **diagnostico_login.py**
    - Diagnóstico de problemas de login
    - Verifica sessões e autenticação

14. **resetar_senha_rapido.py**
    - Script rápido para resetar senha de usuário
    - Útil durante desenvolvimento

15. **temp_diagnostico.py**
    - Script temporário de diagnóstico geral

## 🚀 Como Executar os Testes

### Teste Individual

```bash
# Da pasta raiz do projeto
python testes/test_enhanced_ai.py
```

### Com Ambiente Virtual

```bash
# Windows
.venv/Scripts/python.exe testes/test_enhanced_ai.py

# Linux/Mac
.venv/bin/python testes/test_enhanced_ai.py
```

### Testes Django

```bash
# Testes unitários Django
python manage.py test

# Teste específico
python manage.py test recommendations.tests
```

## 📊 Resultados Esperados

### ✅ Sucesso
- Status 200 OK
- Dados retornados conforme esperado
- Nenhum erro de serialização
- Performance adequada

### ❌ Falha
- Verificar logs no terminal
- Consultar documentação em `documents/troubleshooting/`
- Revisar configurações em `settings.py`

## 📂 Localização

- **Pasta:** `testes/`
- **Projeto:** cgbookstore_v3

## 🔄 Manutenção

- Scripts obsoletos devem ser marcados com `_deprecated` no nome
- Novos testes devem seguir o padrão `test_*.py`
- Documentar propósito no docstring do arquivo

---

**Data de Organização:** 28/10/2025
**Total de Arquivos:** 15 arquivos de teste

# ⚙️ Arquivos de Configuração

Este diretório contém os arquivos de configuração do projeto.

---

## 📁 Arquivos

### 📄 [.env.example](.env.example)

Template de variáveis de ambiente. Copie para `.env` e configure com suas credenciais:

```bash
cp .env.example ../.env
```

**Variáveis Essenciais:**
- `SECRET_KEY` - Chave secreta do Django
- `DEBUG` - Modo debug (False em produção)
- `DATABASE_URL` - URL do PostgreSQL
- `REDIS_URL` - URL do Redis
- `ALLOWED_HOSTS` - Hosts permitidos
- `CSRF_TRUSTED_ORIGINS` - Origins confiáveis para CSRF

**Variáveis Opcionais:**
- OAuth (Google, Facebook)
- APIs (Google Books, Gemini AI)
- Supabase Storage
- Mercado Pago

---

### 📄 [requirements.txt](requirements.txt)

Dependências Python do projeto.

**Instalar:**
```bash
pip install -r requirements.txt
```

**Principais dependências:**
- Django 5.1.1
- PostgreSQL (psycopg2-binary)
- Redis (django-redis)
- Django-allauth (OAuth)
- Google APIs
- Celery
- Gunicorn (produção)
- WhiteNoise (arquivos estáticos)

---

## 🔒 Segurança

### ⚠️ IMPORTANTE

- **NUNCA** commite o arquivo `.env` no Git
- O `.env` já está no `.gitignore`
- Use `.env.example` como referência
- Gere uma `SECRET_KEY` única para produção

### Gerar SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 📚 Documentação Relacionada

- **[Deploy no Render](../docs/deployment/DEPLOY_RENDER.md)**
- **[Guia de Produção](../docs/production/README_PRODUCAO.md)**
- **[Configurar OAuth](../docs/setup/CONFIGURAR_LOGIN_SOCIAL.md)**

---

**Última atualização:** Novembro 2025

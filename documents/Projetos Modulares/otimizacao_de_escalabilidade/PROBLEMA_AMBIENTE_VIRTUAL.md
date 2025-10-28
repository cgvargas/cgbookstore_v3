# SOLUÇÃO: Problema com Ambiente Virtual (.venv)

## PROBLEMA IDENTIFICADO

Quando você tenta rodar `python manage.py runserver` dentro do ambiente virtual `.venv`, ele dá erro:
```
ModuleNotFoundError: No module named 'celery'
```

## CAUSA

O ambiente virtual `.venv` está usando um Python diferente ou não tem as dependências instaladas.

---

## SOLUÇÃO 1: USAR PYTHON GLOBAL (ATUAL - FUNCIONANDO)

✅ **Esta é a solução que está funcionando agora:**

```bash
# NÃO ativar o .venv, usar Python global:
python manage.py runserver
```

O Python global JÁ TEM todas as dependências instaladas e está funcionando perfeitamente!

---

## SOLUÇÃO 2: REINSTALAR NO AMBIENTE VIRTUAL

Se você REALMENTE quer usar o `.venv`, siga estes passos:

### Opção A: Dentro do PowerShell com .venv ativado

```powershell
# Ativar o ambiente virtual
& C:\ProjectsDjango\cgbookstore_v3\.venv\Scripts\Activate.ps1

# Instalar as dependências NO ambiente virtual
pip install -r requirements.txt

# Verificar se instalou
pip list | findstr celery

# Rodar o servidor
python manage.py runserver
```

### Opção B: Especificar o Python do .venv diretamente

```powershell
# Sem ativar o ambiente, usar o executável direto:
C:\ProjectsDjango\cgbookstore_v3\.venv\Scripts\python.exe -m pip install -r requirements.txt
C:\ProjectsDjango\cgbookstore_v3\.venv\Scripts\python.exe manage.py runserver
```

---

## SOLUÇÃO 3: RECRIAR O AMBIENTE VIRTUAL

Se nada funcionar, recrie o ambiente:

```powershell
# Deletar o .venv antigo
Remove-Item -Recurse -Force .venv

# Criar novo ambiente
python -m venv .venv

# Ativar
& .venv\Scripts\Activate.ps1

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Verificar
pip list

# Rodar servidor
python manage.py runserver
```

---

## RECOMENDAÇÃO

**USE O PYTHON GLOBAL!** ✅

Como você já tem todas as dependências instaladas no Python global e está funcionando, recomendo:

1. **NÃO ativar o .venv**
2. **Rodar direto:** `python manage.py runserver`
3. **Tudo funcionará perfeitamente!**

---

## COMANDOS PARA RODAR O PROJETO (USANDO PYTHON GLOBAL)

```bash
# Terminal 1 - Django
python manage.py runserver

# Terminal 2 - Redis (no WSL)
wsl sudo service redis-server start

# Terminal 3 - Celery (opcional)
celery -A cgbookstore worker -l info --pool=solo
```

---

## VERIFICAR QUAL PYTHON ESTÁ SENDO USADO

```bash
# Ver versão e localização do Python
python --version
where python

# Ver se celery está instalado
python -c "import celery; print(celery.__version__)"

# Listar todas as dependências
pip list
```

---

## RESUMO

✅ **SOLUÇÃO ATUAL:** Usar Python global (sem .venv)
⚠️ **SE QUISER .venv:** Reinstalar dependências dentro do ambiente

**O projeto está FUNCIONANDO com o Python global. Recomendo manter assim!**

#!/bin/bash
# Script para iniciar o ambiente de desenvolvimento local

echo "============================================================"
echo "🚀 INICIANDO AMBIENTE LOCAL"
echo "============================================================"
echo ""

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "   Execute primeiro: bash scripts/setup_local_env.sh"
    exit 1
fi

# 1. Verificar/Iniciar Redis
echo "1️⃣  Verificando Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis já está rodando"
else
    echo "   ⏳ Iniciando Redis..."
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "   ✅ Redis iniciado com sucesso"
    else
        echo "   ❌ Falha ao iniciar Redis"
        echo "   💡 Instale o Redis: sudo apt-get install redis-server"
        exit 1
    fi
fi
echo ""

# 2. Verificar Python e dependências
echo "2️⃣  Verificando Python e dependências..."

# Tentar usar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "   Ativando ambiente virtual..."
    source venv/bin/activate 2>/dev/null || true
elif [ -d ".venv" ]; then
    echo "   Ativando ambiente virtual..."
    source .venv/bin/activate 2>/dev/null || true
fi

# Verificar Django
if python3 -c "import django" 2>/dev/null; then
    echo "   ✅ Django instalado"
else
    echo "   ❌ Django não instalado"
    echo "   💡 Instale as dependências: pip install -r requirements.txt"
    exit 1
fi
echo ""

# 3. Aplicar migrações
echo "3️⃣  Aplicando migrações do banco de dados..."
if [ -f manage.py ]; then
    python3 manage.py migrate --noinput 2>&1 | grep -E "(Applying|OK|No migrations|already applied)" | tail -5
    echo "   ✅ Migrações aplicadas"
else
    echo "   ❌ manage.py não encontrado"
    exit 1
fi
echo ""

# 4. Verificar GEMINI_API_KEY
echo "4️⃣  Verificando configuração do Gemini AI..."
if grep -q "^GEMINI_API_KEY=.\+" .env 2>/dev/null; then
    echo "   ✅ GEMINI_API_KEY configurada"
else
    echo "   ⚠️  GEMINI_API_KEY não configurada"
    echo "   💡 Recomendações por IA não funcionarão sem a API key"
    echo "   🔗 Obtenha em: https://aistudio.google.com/app/apikey"
fi
echo ""

# 5. Coletar arquivos estáticos (opcional)
echo "5️⃣  Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear > /dev/null 2>&1
echo "   ✅ Arquivos estáticos coletados"
echo ""

# 6. Iniciar servidor
echo "============================================================"
echo "✅ AMBIENTE PRONTO!"
echo "============================================================"
echo ""
echo "🌐 Iniciando servidor de desenvolvimento..."
echo ""
echo "   URL: http://localhost:8000/"
echo ""
echo "   Pressione Ctrl+C para parar o servidor"
echo ""
echo "============================================================"
echo ""

# Iniciar servidor Django
python3 manage.py runserver

#!/bin/bash
# Script para limpar TODOS os caches (Redis, Django, Browser hints)

echo "============================================================"
echo "🧹 LIMPANDO TODOS OS CACHES"
echo "============================================================"
echo ""

# 1. Limpar cache do Redis
echo "1. Limpando cache do Redis..."
if redis-cli ping > /dev/null 2>&1; then
    redis-cli FLUSHALL
    echo "   ✅ Cache do Redis limpo"
else
    echo "   ⚠️  Redis não está rodando"
fi
echo ""

# 2. Limpar cache de templates do Django
echo "2. Limpando arquivos de cache do Django..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
echo "   ✅ Arquivos .pyc/.pyo removidos"
echo ""

# 3. Recompilar arquivos estáticos
echo "3. Limpando e recoletando arquivos estáticos..."
if [ -d "staticfiles" ]; then
    rm -rf staticfiles/*
    echo "   ✅ Pasta staticfiles limpa"
fi
echo ""

# 4. Adicionar timestamp aos arquivos estáticos (cache busting)
echo "4. Gerando timestamp para cache busting..."
TIMESTAMP=$(date +%s)
echo "   Timestamp: $TIMESTAMP"
echo "   💡 Adicione ?v=$TIMESTAMP às suas URLs estáticas"
echo ""

echo "============================================================"
echo "✅ CACHES LIMPOS COM SUCESSO"
echo "============================================================"
echo ""
echo "⚡ Próximos passos:"
echo "   1. Reinicie o servidor Django:"
echo "      python manage.py runserver"
echo ""
echo "   2. No navegador, faça HARD REFRESH:"
echo "      • Chrome/Edge: Ctrl + Shift + R (Windows/Linux)"
echo "      • Chrome/Edge: Cmd + Shift + R (Mac)"
echo "      • Firefox: Ctrl + F5 (Windows/Linux)"
echo "      • Firefox: Cmd + Shift + R (Mac)"
echo "      • Safari: Cmd + Option + E, depois Cmd + R"
echo ""
echo "   3. Ou limpe o cache do navegador:"
echo "      • Chrome: Settings > Privacy > Clear browsing data"
echo "      • Firefox: Settings > Privacy > Clear Data"
echo ""
echo "============================================================"

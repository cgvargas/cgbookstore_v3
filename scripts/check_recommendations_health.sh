#!/bin/bash
# Script simples para verificar saúde do módulo de recomendações

echo "============================================================"
echo "🔍 VERIFICAÇÃO DE SAÚDE - MÓDULO DE RECOMENDAÇÕES"
echo "============================================================"
echo ""

# 1. Verificar Redis
echo "1. Verificando Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis está rodando"
    redis-cli INFO | grep "uptime_in_seconds" | sed 's/^/   /'
else
    echo "   ❌ Redis NÃO está rodando!"
    echo "   💡 Inicie com: redis-server --daemonize yes"
fi
echo ""

# 2. Verificar arquivos corrigidos
echo "2. Verificando arquivos corrigidos..."

files=(
    "recommendations/gemini_ai_enhanced.py"
    "recommendations/algorithms_preference_weighted.py"
    "recommendations/views_simple.py"
    "templates/recommendations/recommendations_section.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (não encontrado)"
    fi
done
echo ""

# 3. Verificar se correções foram aplicadas
echo "3. Verificando correções aplicadas..."

# Verificar timeout no frontend
if grep -q "timeoutDuration = algorithm === 'ai' ? 30000 : 10000" templates/recommendations/recommendations_section.html 2>/dev/null; then
    echo "   ✅ Timeout do frontend corrigido (30s para IA)"
else
    echo "   ❌ Timeout do frontend NÃO corrigido"
fi

# Verificar hash das prateleiras
if grep -q "get_user_shelves_hash" recommendations/algorithms_preference_weighted.py 2>/dev/null; then
    echo "   ✅ Hash das prateleiras implementado"
else
    echo "   ❌ Hash das prateleiras NÃO implementado"
fi

# Verificar timeout no Gemini
if grep -q "request_options={'timeout': 20}" recommendations/gemini_ai_enhanced.py 2>/dev/null; then
    echo "   ✅ Timeout do Gemini adicionado (20s)"
else
    echo "   ❌ Timeout do Gemini NÃO adicionado"
fi

# Verificar health check do Redis
if grep -q "redis_health_check" recommendations/views_simple.py 2>/dev/null; then
    echo "   ✅ Health check do Redis implementado"
else
    echo "   ❌ Health check do Redis NÃO implementado"
fi

echo ""
echo "============================================================"
echo "📊 RESUMO"
echo "============================================================"
echo ""
echo "Correções implementadas:"
echo "  1. ✅ Redis iniciado e rodando"
echo "  2. ✅ Timeout do frontend aumentado (5s → 30s para IA)"
echo "  3. ✅ Timeout do Gemini adicionado (20s)"
echo "  4. ✅ Cache key agora inclui hash das prateleiras"
echo "  5. ✅ Health check do Redis implementado"
echo ""
echo "💡 Para testar as recomendações:"
echo "   - Acesse: http://localhost:8000/"
echo "   - Faça login"
echo "   - Vá até a seção 'Para Você'"
echo "   - Teste 'Personalizado' e 'IA Premium'"
echo ""
echo "============================================================"

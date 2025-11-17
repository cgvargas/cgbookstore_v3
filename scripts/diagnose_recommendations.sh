#!/bin/bash
# Script de Diagnóstico Completo do Módulo de Recomendações

echo "============================================================"
echo "🔍 DIAGNÓSTICO COMPLETO - MÓDULO DE RECOMENDAÇÕES"
echo "============================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success=0
warnings=0
errors=0

# Função para printar status
print_status() {
    local status=$1
    local message=$2

    case $status in
        "ok")
            echo -e "${GREEN}✅ $message${NC}"
            ((success++))
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ((warnings++))
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ((errors++))
            ;;
        *)
            echo "   $message"
            ;;
    esac
}

# 1. VERIFICAR REDIS
echo "1️⃣  VERIFICANDO REDIS"
echo "─────────────────────────────────────────────────────────"
if redis-cli ping > /dev/null 2>&1; then
    print_status "ok" "Redis está rodando"
    redis-cli INFO | grep -E "uptime_in_seconds|used_memory_human" | sed 's/^/   /'
else
    print_status "error" "Redis NÃO está rodando"
    echo "   💡 Inicie com: redis-server --daemonize yes"
fi
echo ""

# 2. VERIFICAR VARIÁVEIS DE AMBIENTE
echo "2️⃣  VERIFICANDO VARIÁVEIS DE AMBIENTE"
echo "─────────────────────────────────────────────────────────"
if [ -f .env ]; then
    print_status "ok" "Arquivo .env existe"

    # Verificar variáveis críticas
    if grep -q "^GEMINI_API_KEY=" .env 2>/dev/null; then
        key_value=$(grep "^GEMINI_API_KEY=" .env | cut -d= -f2)
        if [ -n "$key_value" ] && [ "$key_value" != "''" ] && [ "$key_value" != '""' ]; then
            print_status "ok" "GEMINI_API_KEY configurada"
        else
            print_status "error" "GEMINI_API_KEY está vazia"
        fi
    else
        print_status "error" "GEMINI_API_KEY não encontrada no .env"
    fi

    if grep -q "^REDIS_URL=" .env 2>/dev/null; then
        print_status "ok" "REDIS_URL configurada"
    else
        print_status "warning" "REDIS_URL não configurada (usará padrão)"
    fi

    if grep -q "^DEBUG=" .env 2>/dev/null; then
        debug_value=$(grep "^DEBUG=" .env | cut -d= -f2)
        print_status "info" "DEBUG=$debug_value"
    fi
else
    print_status "error" "Arquivo .env NÃO existe"
    echo ""
    echo "   💡 SOLUÇÃO: Crie o arquivo .env com as variáveis necessárias"
    echo "   Exemplo mínimo:"
    echo "   ────────────────────────────────────────────────"
    echo "   SECRET_KEY=sua-secret-key-aqui"
    echo "   DEBUG=True"
    echo "   GEMINI_API_KEY=sua-api-key-do-gemini-aqui"
    echo "   REDIS_URL=redis://127.0.0.1:6379/1"
    echo "   DATABASE_URL=sqlite:///db.sqlite3"
    echo "   ────────────────────────────────────────────────"
    echo ""
    echo "   🔑 Para obter a GEMINI_API_KEY:"
    echo "   1. Acesse: https://aistudio.google.com/app/apikey"
    echo "   2. Faça login com sua conta Google"
    echo "   3. Clique em 'Create API Key'"
    echo "   4. Copie a chave e cole no .env"
    echo ""
fi
echo ""

# 3. VERIFICAR ARQUIVOS DO MÓDULO
echo "3️⃣  VERIFICANDO ARQUIVOS DO MÓDULO"
echo "─────────────────────────────────────────────────────────"
files=(
    "recommendations/views_simple.py"
    "recommendations/gemini_ai_enhanced.py"
    "recommendations/algorithms_preference_weighted.py"
    "recommendations/urls.py"
    "templates/recommendations/recommendations_section.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_status "ok" "$file"
    else
        print_status "error" "$file (não encontrado)"
    fi
done
echo ""

# 4. VERIFICAR CORREÇÕES IMPLEMENTADAS
echo "4️⃣  VERIFICANDO CORREÇÕES IMPLEMENTADAS"
echo "─────────────────────────────────────────────────────────"

# Timeout do frontend
if grep -q "timeoutDuration = algorithm === 'ai' ? 30000 : 10000" templates/recommendations/recommendations_section.html 2>/dev/null; then
    print_status "ok" "Timeout do frontend corrigido (30s para IA)"
else
    print_status "error" "Timeout do frontend NÃO corrigido"
fi

# Hash das prateleiras
if grep -q "get_user_shelves_hash" recommendations/algorithms_preference_weighted.py 2>/dev/null; then
    print_status "ok" "Hash das prateleiras implementado"
else
    print_status "error" "Hash das prateleiras NÃO implementado"
fi

# Timeout do Gemini
if grep -q "request_options={'timeout': 20}" recommendations/gemini_ai_enhanced.py 2>/dev/null; then
    print_status "ok" "Timeout do Gemini implementado (20s)"
else
    print_status "error" "Timeout do Gemini NÃO implementado"
fi

# Health check do Redis
if grep -q "redis_health_check" recommendations/views_simple.py 2>/dev/null; then
    print_status "ok" "Health check do Redis implementado"
else
    print_status "error" "Health check do Redis NÃO implementado"
fi
echo ""

# 5. VERIFICAR SERVIDOR DJANGO
echo "5️⃣  VERIFICANDO SERVIDOR DJANGO"
echo "─────────────────────────────────────────────────────────"
if pgrep -f "manage.py runserver" > /dev/null 2>&1; then
    print_status "ok" "Servidor Django está rodando"
    port=$(ps aux | grep "manage.py runserver" | grep -v grep | grep -oP ':\d+' | head -1 | tr -d ':')
    if [ -n "$port" ]; then
        echo "   Porta: $port"
    fi
else
    print_status "warning" "Servidor Django NÃO está rodando"
    echo "   💡 Inicie com: python manage.py runserver"
fi
echo ""

# 6. VERIFICAR BANCO DE DADOS
echo "6️⃣  VERIFICANDO BANCO DE DADOS"
echo "─────────────────────────────────────────────────────────"
if [ -f db.sqlite3 ]; then
    print_status "ok" "Banco de dados SQLite existe"
    size=$(du -h db.sqlite3 | cut -f1)
    echo "   Tamanho: $size"
else
    print_status "warning" "Banco de dados SQLite não encontrado"
    echo "   💡 Execute: python manage.py migrate"
fi
echo ""

# 7. VERIFICAR DEPENDÊNCIAS PYTHON
echo "7️⃣  VERIFICANDO DEPENDÊNCIAS PYTHON"
echo "─────────────────────────────────────────────────────────"
python3 -c "import django; print('Django:', django.__version__)" 2>/dev/null && print_status "ok" "Django instalado" || print_status "error" "Django NÃO instalado"
python3 -c "import google.generativeai; print('google-generativeai instalado')" 2>/dev/null && print_status "ok" "google-generativeai instalado" || print_status "error" "google-generativeai NÃO instalado"
python3 -c "import redis; print('redis-py instalado')" 2>/dev/null && print_status "ok" "redis-py instalado" || print_status "error" "redis-py NÃO instalado"
python3 -c "import django_redis; print('django-redis instalado')" 2>/dev/null && print_status "ok" "django-redis instalado" || print_status "error" "django-redis NÃO instalado"
echo ""

# RESUMO FINAL
echo "============================================================"
echo "📊 RESUMO DO DIAGNÓSTICO"
echo "============================================================"
echo -e "${GREEN}✅ Sucessos: $success${NC}"
echo -e "${YELLOW}⚠️  Avisos: $warnings${NC}"
echo -e "${RED}❌ Erros: $errors${NC}"
echo ""

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 TUDO OK! O módulo de recomendações deve estar funcionando.${NC}"
    echo ""
    echo "📝 PRÓXIMOS PASSOS:"
    echo "   1. Inicie o servidor: python manage.py runserver"
    echo "   2. Acesse: http://localhost:8000/"
    echo "   3. Faça login e teste as recomendações"
else
    echo -e "${RED}⚠️  PROBLEMAS ENCONTRADOS! Corrija os erros acima antes de testar.${NC}"
    echo ""
    echo "🔧 CHECKLIST DE CORREÇÕES:"
    echo "   [ ] Redis rodando: redis-server --daemonize yes"
    echo "   [ ] Arquivo .env criado com GEMINI_API_KEY"
    echo "   [ ] Dependências instaladas: pip install -r requirements.txt"
    echo "   [ ] Migrações aplicadas: python manage.py migrate"
    echo "   [ ] Servidor rodando: python manage.py runserver"
fi
echo ""
echo "============================================================"

exit $errors

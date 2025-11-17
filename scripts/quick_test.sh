#!/bin/bash

#####################################################################
# Quick Test - Configuração e Teste Rápido
# Automatiza todos os passos necessários para testar localmente
#####################################################################

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════"
echo "  ⚡ QUICK TEST - Setup Automático"
echo "  Configura e testa a branch integrada"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}\n"

#####################################################################
# 1. Validar Branch
#####################################################################
echo -e "${BLUE}[1/7]${NC} Validando branch..."
if bash scripts/test_integrated_branch.sh > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Validação passou!"
else
    echo -e "  ${RED}✗${NC} Validação falhou. Executando diagnóstico completo...\n"
    bash scripts/test_integrated_branch.sh
    exit 1
fi

#####################################################################
# 2. Configurar .env
#####################################################################
echo -e "\n${BLUE}[2/7]${NC} Configurando arquivo .env..."

if [ ! -f ".env" ]; then
    echo -e "  ${YELLOW}→${NC} Criando .env a partir do template..."
    bash scripts/setup_local_env.sh > /dev/null 2>&1
    echo -e "  ${GREEN}✓${NC} Arquivo .env criado!"

    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  ⚠️  IMPORTANTE: Configure sua GEMINI_API_KEY${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "\n1. Acesse: ${CYAN}https://aistudio.google.com/app/apikey${NC}"
    echo -e "2. Crie uma API Key"
    echo -e "3. Edite o arquivo .env e cole sua chave:\n"
    echo -e "   ${CYAN}nano .env${NC}  # ou use seu editor favorito\n"
    echo -e "   Encontre: ${YELLOW}GEMINI_API_KEY=${NC}"
    echo -e "   Cole:     ${GREEN}GEMINI_API_KEY=AIzaSyA_sua_chave_aqui${NC}\n"

    read -p "Pressione ENTER depois de configurar a GEMINI_API_KEY..."
else
    echo -e "  ${GREEN}✓${NC} Arquivo .env já existe"

    # Verificar se GEMINI_API_KEY está configurada
    if grep -q "GEMINI_API_KEY=AIza" .env 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} GEMINI_API_KEY configurada"
    else
        echo -e "  ${YELLOW}⚠${NC} GEMINI_API_KEY não configurada ou vazia"
        echo -e "  ${YELLOW}→${NC} Edite .env e adicione sua chave: ${CYAN}nano .env${NC}"
        read -p "Pressione ENTER depois de configurar..."
    fi
fi

#####################################################################
# 3. Instalar Dependências
#####################################################################
echo -e "\n${BLUE}[3/7]${NC} Instalando dependências Python..."

PYTHON_CMD=$(command -v python3 || command -v python)

if ! $PYTHON_CMD -c "import django" 2>/dev/null; then
    echo -e "  ${YELLOW}→${NC} Instalando dependências (isso pode demorar)..."
    pip install -q -r requirements.txt
    echo -e "  ${GREEN}✓${NC} Dependências instaladas!"
else
    echo -e "  ${GREEN}✓${NC} Dependências já instaladas"
fi

#####################################################################
# 4. Iniciar Redis
#####################################################################
echo -e "\n${BLUE}[4/7]${NC} Iniciando Redis..."

if command -v redis-server &> /dev/null; then
    if ! redis-cli ping &> /dev/null; then
        echo -e "  ${YELLOW}→${NC} Iniciando Redis server..."
        redis-server --daemonize yes 2>/dev/null
        sleep 2

        if redis-cli ping &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} Redis iniciado com sucesso!"
        else
            echo -e "  ${RED}✗${NC} Falha ao iniciar Redis"
            echo -e "  ${YELLOW}→${NC} Tente manualmente: redis-server --daemonize yes"
        fi
    else
        echo -e "  ${GREEN}✓${NC} Redis já está rodando"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Redis não instalado"
    echo -e "  ${YELLOW}→${NC} Ubuntu/Debian: sudo apt-get install redis-server"
    echo -e "  ${YELLOW}→${NC} macOS: brew install redis"
    echo -e "  ${YELLOW}→${NC} Continuando sem Redis (performance reduzida)..."
fi

#####################################################################
# 5. Limpar Cache
#####################################################################
echo -e "\n${BLUE}[5/7]${NC} Limpando cache antigo..."

if redis-cli ping &> /dev/null; then
    redis-cli FLUSHALL > /dev/null 2>&1
    echo -e "  ${GREEN}✓${NC} Cache do Redis limpo!"
else
    echo -e "  ${YELLOW}⚠${NC} Redis não disponível - pulando limpeza de cache"
fi

# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo -e "  ${GREEN}✓${NC} Cache Python limpo!"

#####################################################################
# 6. Aplicar Migrações
#####################################################################
echo -e "\n${BLUE}[6/7]${NC} Aplicando migrações do banco de dados..."

$PYTHON_CMD manage.py migrate --no-input > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Migrações aplicadas com sucesso!"
else
    echo -e "  ${YELLOW}⚠${NC} Algumas migrações podem ter falhado (verifique acima)"
fi

#####################################################################
# 7. Iniciar Servidor
#####################################################################
echo -e "\n${BLUE}[7/7]${NC} Iniciando servidor Django..."

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Setup completo! Iniciando servidor...${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📋 Checklist de Testes:${NC}\n"
echo -e "  1. ${CYAN}http://localhost:8000/${NC} - Abra no navegador"
echo -e "  2. Faça login"
echo -e "  3. Adicione livros às prateleiras (Favoritos, Lidos)"
echo -e "  4. Role até 'Para Você' na home"
echo -e "  5. Teste 'Personalizado' (< 2s)"
echo -e "  6. Teste 'IA Premium' (< 40s na primeira vez, < 1s depois)"
echo -e "  7. Verifique design (Banner, Cards, Navbar)\n"

echo -e "${YELLOW}🐛 Dica: Abra DevTools (F12) para ver logs detalhados${NC}\n"

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

# Iniciar servidor
$PYTHON_CMD manage.py runserver

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Servidor encerrado. Até logo! 👋${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

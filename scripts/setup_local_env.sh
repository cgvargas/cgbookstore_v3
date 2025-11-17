#!/bin/bash
# Script para configurar ambiente local de desenvolvimento

echo "============================================================"
echo "🚀 CONFIGURAÇÃO DO AMBIENTE LOCAL"
echo "============================================================"
echo ""

# 1. Criar arquivo .env se não existir
if [ -f .env ]; then
    echo "⚠️  Arquivo .env já existe!"
    read -p "   Deseja sobrescrever? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operação cancelada."
        exit 1
    fi
fi

echo "📝 Criando arquivo .env..."

# Gerar SECRET_KEY aleatória
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Criar .env com valores para desenvolvimento local
cat > .env << EOF
# =============================================================================
# Django Settings
# =============================================================================
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# =============================================================================
# Database Configuration (SQLite para desenvolvimento)
# =============================================================================
DATABASE_URL=sqlite:///db.sqlite3

# =============================================================================
# Redis Configuration
# =============================================================================
REDIS_URL=redis://127.0.0.1:6379/1

# =============================================================================
# Gemini AI API (OBRIGATÓRIO para recomendações por IA)
# =============================================================================
# 🔑 ATENÇÃO: Configure sua API key do Gemini aqui!
# Como obter: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=

# =============================================================================
# Email Configuration (Console para desenvolvimento)
# =============================================================================
DEFAULT_FROM_EMAIL=noreply@cgbookstore.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
USE_BREVO_API=False

# =============================================================================
# Optional APIs (não obrigatórias para desenvolvimento local)
# =============================================================================
# Google Books API (para buscar dados de livros)
GOOGLE_BOOKS_API_KEY=

# Supabase (para storage de imagens - opcional)
USE_SUPABASE_STORAGE=False
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# Social Auth (Google e Facebook - opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# Mercado Pago (para pagamentos - opcional)
MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_PUBLIC_KEY=

# Site URL
SITE_URL=http://localhost:8000
EOF

echo "✅ Arquivo .env criado com sucesso!"
echo ""

# 2. Mostrar próximos passos
echo "============================================================"
echo "📋 PRÓXIMOS PASSOS"
echo "============================================================"
echo ""
echo "🔴 OBRIGATÓRIO:"
echo ""
echo "1. Configure a GEMINI_API_KEY no arquivo .env"
echo "   🔗 Obtenha sua chave em: https://aistudio.google.com/app/apikey"
echo "   "
echo "   Edite o arquivo .env e substitua:"
echo "   GEMINI_API_KEY="
echo "   "
echo "   Por:"
echo "   GEMINI_API_KEY=sua-chave-aqui"
echo ""
echo "─────────────────────────────────────────────────────────"
echo ""
echo "🟢 RECOMENDADO (mas opcional):"
echo ""
echo "2. Configure outras APIs conforme necessário:"
echo "   • GOOGLE_BOOKS_API_KEY - Para buscar dados de livros"
echo "   • SUPABASE - Para storage de imagens em produção"
echo "   • Social Auth - Para login com Google/Facebook"
echo "   • Mercado Pago - Para processar pagamentos"
echo ""
echo "============================================================"
echo ""
echo "✅ Configuração básica concluída!"
echo ""
echo "⚡ Para testar as recomendações localmente:"
echo "   1. Configure GEMINI_API_KEY no .env"
echo "   2. Execute: bash scripts/start_local.sh"
echo ""
echo "============================================================"

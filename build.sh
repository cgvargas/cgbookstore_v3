#!/usr/bin/env bash
# Build script para Render.com
set -o errexit  # Exit on error

echo "🚀 Iniciando build para Render..."

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Executar migrations
echo "🗄️ Executando migrations..."
python manage.py migrate --no-input

echo "✅ Build concluído com sucesso!"

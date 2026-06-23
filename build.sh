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

# Configurar Site domain (crítico para allauth funcionar corretamente)
# Sem isso, o Site fica com "localhost:8000" e login pode falhar
echo "🌐 Configurando Site domain..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()
from django.contrib.sites.models import Site
domain = os.getenv('SITE_DOMAIN', 'www.cgbookstore.com.br')
name = os.getenv('SITE_NAME', 'CG Bookstore')
site, created = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': name})
if not created:
    if site.domain != domain or site.name != name:
        old_domain = site.domain
        site.domain = domain
        site.name = name
        site.save()
        print(f'  Site atualizado: {old_domain} -> {domain}')
    else:
        print(f'  Site já configurado: {domain}')
else:
    print(f'  Site criado: {domain}')
"

echo "✅ Build concluído com sucesso!"

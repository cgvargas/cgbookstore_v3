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

# Remover Sites duplicados que tenham o mesmo domain mas id diferente de 1
duplicates = Site.objects.filter(domain=domain).exclude(id=1)
if duplicates.exists():
    print(f'  Removendo {duplicates.count()} Site(s) duplicado(s) com domain={domain}')
    duplicates.delete()

# Agora atualizar ou criar o Site id=1
site, created = Site.objects.update_or_create(
    id=1,
    defaults={'domain': domain, 'name': name}
)
if created:
    print(f'  Site criado: {domain}')
else:
    print(f'  Site configurado: {domain} (name={name})')
"

# Limpar cache para garantir que as atualizações do deploy sejam refletidas imediatamente
echo "🧹 Limpando cache do sistema..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()
from django.core.cache import cache
try:
    cache.clear()
    print('  Cache limpo com sucesso!')
except Exception as e:
    print(f'  Erro ao limpar cache: {e}')
"

echo "✅ Build concluído com sucesso!"

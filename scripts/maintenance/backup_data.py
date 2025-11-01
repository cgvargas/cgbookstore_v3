import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')

# Temporariamente usar SQLite
import cgbookstore.settings as settings
settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': settings.BASE_DIR / 'db.sqlite3',
    }
}

django.setup()

from django.core import serializers
from django.contrib.auth import get_user_model
from core.models import Category, Author, Book

User = get_user_model()

# Coletar dados
data = []
data.extend(User.objects.all())
data.extend(Category.objects.all())
data.extend(Author.objects.all())
data.extend(Book.objects.all())

# Serializar
json_data = serializers.serialize('json', data, indent=2, use_natural_foreign_keys=False)

# Salvar
with open('backup_sqlite_data.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

print(f'✅ Backup criado: {len(data)} objetos')
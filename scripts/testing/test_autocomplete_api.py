import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.views.section_autocomplete import section_item_autocomplete

User = get_user_model()
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.create_superuser('testadmin_temp', 'admin_temp@admin.com', 'admin')

factory = RequestFactory()
request = factory.get('/admin-tools/section-autocomplete/?q=a&content_type=article')
request.user = user

response = section_item_autocomplete(request)
print("Status Code:", response.status_code)
print("Content:", response.content.decode('utf-8'))

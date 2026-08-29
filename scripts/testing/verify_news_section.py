import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
project_root = r"c:\ProjectDjango\cgbookstore_v3"
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Section, SectionItem
from news.models import Article, Category

def verify_news_section():
    print("Verifying News Section Implementation...")
    
    User = get_user_model()
    admin_user, _ = User.objects.get_or_create(username='admin_test', defaults={'email': 'admin@test.com', 'is_staff': True, 'is_superuser': True})

    # 1. Create News Category
    category, _ = Category.objects.get_or_create(name='Test News', slug='test-news', color='#ff0000')
    
    # 2. Create Articles
    article1, _ = Article.objects.get_or_create(
        title='Test Article 1',
        slug='test-article-1',
        defaults={
            'author': admin_user,
            'category': category,
            'excerpt': 'This is a test article excerpt 1.',
            'content': 'Full content 1',
            'is_published': True,
            'published_at': timezone.now()
        }
    )
    
    article2, _ = Article.objects.get_or_create(
        title='Test Article 2',
        slug='test-article-2',
        defaults={
            'author': admin_user,
            'category': category,
            'excerpt': 'This is a test article excerpt 2.',
            'content': 'Full content 2',
            'is_published': True,
            'published_at': timezone.now()
        }
    )
    print(f"Created/Found articles: {article1.title}, {article2.title}")

    # 3. Create News Section
    section, created = Section.objects.get_or_create(
        title='Latest News',
        defaults={
            'content_type': 'news',
            'layout': 'carousel',
            'active': True,
            'order': 0
        }
    )
    if not created:
        section.content_type = 'news'
        section.layout = 'carousel'
        section.active = True
        section.save()
    print(f"Created/Updated section: {section.title}")

    # 4. Add items to section
    # Clear existing items to avoid duplicates for this test
    section.items.all().delete()
    
    SectionItem.objects.create(section=section, content_object=article1, order=1)
    SectionItem.objects.create(section=section, content_object=article2, order=2)
    print("Added articles to section.")

    # 5. Verify on Homepage
    client = Client()
    response = client.get('/')
    
    if response.status_code != 200:
        print(f"FAILED: Homepage returned status {response.status_code}")
        return False
        
    content = response.content.decode('utf-8')
    
    if 'Latest News' in content:
        print("SUCCESS: Section title found on homepage.")
    else:
        print("FAILED: Section title NOT found on homepage.")
        return False
        
    if 'Test Article 1' in content:
        print("SUCCESS: Article 1 found on homepage.")
    else:
        print("FAILED: Article 1 NOT found on homepage.")
        return False
        
    if 'Test Article 2' in content:
        print("SUCCESS: Article 2 found on homepage.")
    else:
        print("FAILED: Article 2 NOT found on homepage.")
        return False
        
    if 'test-article-1' in content:
        print("SUCCESS: Article 1 link found.")
    else:
        print("FAILED: Article 1 link NOT found.")
        return False

    # Clean up (optional, maybe better to leave for manual inspection if needed)
    # section.delete()
    # article1.delete()
    # article2.delete()
    
    print("Verification Passed!")
    return True

if __name__ == "__main__":
    verify_news_section()

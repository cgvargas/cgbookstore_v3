from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Section, SectionItem
from news.models import Article, Category

class Command(BaseCommand):
    help = 'Verify News Section Implementation'

    def handle(self, *args, **kwargs):
        self.stdout.write("Verifying News Section Implementation...")
        
        User = get_user_model()
        # Use existing user or create one
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin_test_verify', 'admin@test.com', 'password')

        # 1. Create News Category
        category, _ = Category.objects.get_or_create(name='Test News Verify', slug='test-news-verify', defaults={'color': '#ff0000'})
        
        # 2. Create Articles
        article1, _ = Article.objects.get_or_create(
            title='Test Article Verify 1',
            slug='test-article-verify-1',
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
            title='Test Article Verify 2',
            slug='test-article-verify-2',
            defaults={
                'author': admin_user,
                'category': category,
                'excerpt': 'This is a test article excerpt 2.',
                'content': 'Full content 2',
                'is_published': True,
                'published_at': timezone.now()
            }
        )
        self.stdout.write(f"Created/Found articles: {article1.title}, {article2.title}")

        # 3. Create News Section
        section, created = Section.objects.get_or_create(
            title='Latest News Verify',
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
        self.stdout.write(f"Created/Updated section: {section.title}")

        # 4. Add items to section
        # Clear existing items to avoid duplicates for this test
        section.items.all().delete()
        
        SectionItem.objects.create(section=section, content_object=article1, order=1)
        SectionItem.objects.create(section=section, content_object=article2, order=2)
        self.stdout.write("Added articles to section.")

        # 5. Verify on Homepage
        client = Client()
        try:
            response = client.get('/', HTTP_HOST='127.0.0.1')
            self.stdout.write(f"Homepage status: {response.status_code}")
        except Exception as e:
            self.stdout.write(f"Error fetching homepage: {e}")
            return
        
        if response.status_code != 200:
            self.stdout.write(f"FAILED: Homepage returned status {response.status_code}")
            return
            
        content = response.content.decode('utf-8')
        
        success = True
        
        if 'Latest News Verify' in content:
            self.stdout.write("SUCCESS: Section title found on homepage.")
        else:
            self.stdout.write("FAILED: Section title NOT found on homepage.")
            success = False
            
        if 'Test Article Verify 1' in content:
            self.stdout.write("SUCCESS: Article 1 found on homepage.")
        else:
            self.stdout.write("FAILED: Article 1 NOT found on homepage.")
            success = False
            
        if 'Test Article Verify 2' in content:
            self.stdout.write("SUCCESS: Article 2 found on homepage.")
        else:
            self.stdout.write("FAILED: Article 2 NOT found on homepage.")
            success = False
            
        # Check link presence (partial match is enough usually)
        if 'test-article-verify-1' in content:
            self.stdout.write("SUCCESS: Article 1 link found.")
        else:
            self.stdout.write("FAILED: Article 1 link NOT found.")
            success = False

        if success:
            self.stdout.write(self.style.SUCCESS("Verification Passed!"))
        else:
            self.stdout.write(self.style.ERROR("Verification Failed!"))

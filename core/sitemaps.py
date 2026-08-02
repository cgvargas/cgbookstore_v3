from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import Book, Author, Category
from news.models import Article

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:book_list',
            'core:author_list',
            'core:about',
            'core:contact',
            'core:faq',
            'core:events',
            'core:terms',
            'core:privacy',
            'news:home',
            'news:all_articles',
        ]

    def location(self, item):
        return reverse(item)


class BookSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Book.objects.filter(active=True)

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)

    def location(self, obj):
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return reverse('core:book_detail', kwargs={'slug': obj.slug})


class AuthorSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Author.objects.all()

    def location(self, obj):
        return reverse('core:author_detail', kwargs={'pk': obj.pk})


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"/livros/?categoria={obj.slug}"


class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'published_at', None)

    def location(self, obj):
        return reverse('news:article_detail', kwargs={'slug': obj.slug})

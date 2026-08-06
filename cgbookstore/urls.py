from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse
from core.views import copyright_views

from django.contrib.sitemaps.views import sitemap
from core.sitemaps import (
    StaticViewSitemap,
    BookSitemap,
    AuthorSitemap,
    CategorySitemap,
    ArticleSitemap,
    LiteraryUniverseSitemap,
)

sitemaps = {
    'static': StaticViewSitemap,
    'books': BookSitemap,
    'authors': AuthorSitemap,
    'categories': CategorySitemap,
    'articles': ArticleSitemap,
    'universes': LiteraryUniverseSitemap,
}

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /admin-tools/",
        "Disallow: /accounts/",
        "Disallow: /profile/",
        "Disallow: /api/",
        "Allow: /",
        "",
        "Sitemap: https://www.cgbookstore.com.br/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/product-analytics/', include('product_analytics.urls', namespace='product_analytics')),
    path('admin/audit/image-copyright/', copyright_views.copyright_audit_dashboard, name='copyright_audit_dashboard'),
    path('admin/audit/image-copyright/compliance-map/', copyright_views.copyright_compliance_map, name='copyright_compliance_map'),
    path('admin/copyright-doc/<int:record_id>/', copyright_views.protected_copyright_document_download, name='protected_copyright_document'),
    path('admin/', admin.site.urls),

    # Ferramentas administrativas (sem necessidade de Shell)
    path('admin-tools/', include('core.urls_admin_tools', namespace='admin_tools')),

    # Django-allauth URLs (ANTES de accounts/)
    path('accounts/', include('allauth.urls')),

    # Nossas URLs customizadas (profile, etc.)
    path('profile/', include('accounts.urls', namespace='accounts')),

    path('chatbot/', include('chatbot_literario.urls', namespace='chatbot')),
    path('debates/', include('debates.urls')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('novos-autores/', include('new_authors.urls', namespace='new_authors')),
    path('noticias/', include('news.urls', namespace='news')),
    path('ereader/', include('ereader.urls', namespace='ereader')),
    path('api/ereader/', include('ereader.api_urls', namespace='ereader_api')),
    path('partners/', include('partners.urls', namespace='partners')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('core.urls', namespace='core')),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
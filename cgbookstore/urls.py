from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /profile/",
        "Disallow: /api/",
        "Sitemap: https://www.cgbookstore.com.br/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.cgbookstore.com.br/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://www.cgbookstore.com.br/livros/</loc>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://www.cgbookstore.com.br/autores/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.cgbookstore.com.br/noticias/</loc>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://www.cgbookstore.com.br/sobre/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
</urlset>"""
    return HttpResponse(xml_content.strip(), content_type="application/xml")

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('admin/product-analytics/', include('product_analytics.urls', namespace='product_analytics')),
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
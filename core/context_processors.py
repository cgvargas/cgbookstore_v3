from django.conf import settings

def seo_context(request):
    """
    Context Processor global para SEO Técnico:
    - URL Canônica base
    - Open Graph por omissão
    - Twitter Cards
    - Dados da Organização
    """
    full_path = request.get_full_path()
    # Remover query parameters irrelevantes para a URL canônica por padrão
    clean_path = request.path
    
    canonical_url = f"https://www.cgbookstore.com.br{clean_path}"
    
    return {
        'SEO_CANONICAL_URL': canonical_url,
        'SEO_SITE_NAME': 'CG.BookStore',
        'SEO_DEFAULT_TITLE': 'CG.BookStore - Sua Biblioteca Digital & Comunidade Literária',
        'SEO_DEFAULT_DESCRIPTION': 'Descubra livros incríveis, gerencie sua biblioteca pessoal, receba recomendações por IA e participe de debates literários.',
        'SEO_DEFAULT_OG_IMAGE': 'https://www.cgbookstore.com.br/static/images/logo_appweb.png',
        'SEO_TWITTER_HANDLE': '@cgbookstore',
    }

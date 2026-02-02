"""
Views administrativas para executar comandos sem acesso ao Shell.
Útil para plano free do Render que não tem Shell access.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.db import connection
from django.contrib.sites.models import Site
from django.conf import settings
from core.models import Category, Book, Author
from allauth.socialaccount.models import SocialApp
import io
import sys


def redis_test_view(request):
    """
    Endpoint PÚBLICO para testar conexão com Redis.
    Não requer login - para diagnóstico rápido em produção.
    Acesse: /api/redis-test/
    """
    import time
    from django.core.cache import cache
    
    result = {
        'redis_url_configured': bool(settings.CACHES.get('default', {}).get('LOCATION')),
        'redis_url': settings.CACHES.get('default', {}).get('LOCATION', 'NOT SET')[:50] + '...',
    }
    
    try:
        start = time.time()
        # Testar escrita
        cache.set('redis_test_key', 'test_value_123', timeout=30)
        # Testar leitura
        value = cache.get('redis_test_key')
        elapsed = (time.time() - start) * 1000
        
        if value == 'test_value_123':
            result['status'] = 'OK'
            result['message'] = f'Redis funcionando! ({elapsed:.1f}ms)'
            result['cache_working'] = True
        else:
            result['status'] = 'ERROR'
            result['message'] = f'Redis retornou valor incorreto: {value}'
            result['cache_working'] = False
    except Exception as e:
        result['status'] = 'ERROR'
        result['message'] = f'Redis não conectou: {str(e)}'
        result['cache_working'] = False
        result['error_type'] = type(e).__name__
    
    return JsonResponse(result)


@staff_member_required
@require_http_methods(["GET", "POST"])
def setup_initial_data_view(request):
    """
    View para executar o comando setup_initial_data via browser.
    Acessível apenas para staff/superuser.
    """
    output = []
    success = False

    if request.method == "POST":
        # Capturar output do comando
        out = io.StringIO()

        try:
            # Executar comando
            call_command('setup_initial_data',
                        skip_superuser=True,  # Não criar superuser via web
                        stdout=out)

            output_text = out.getvalue()
            output = output_text.split('\n')
            success = True

        except Exception as e:
            output = [f"❌ Erro ao executar comando: {str(e)}"]
            success = False

    # Se GET, mostrar status atual
    stats = {
        'site_configured': Site.objects.filter(id=1).exists(),
        'categories_count': Category.objects.count(),
        'books_count': Book.objects.count(),
        'social_apps_count': SocialApp.objects.count(),
        'db_connected': check_database_connection(),
    }

    context = {
        'stats': stats,
        'output': output,
        'success': success,
        'post_url': request.path,
    }

    return render(request, 'admin_tools/setup_initial_data.html', context)


@staff_member_required
def health_check_view(request):
    """
    View para executar health check via browser.
    Acessível apenas para staff/superuser.
    """
    results = {
        'database': check_database(),
        'redis': check_redis(),
        'site': check_site(),
        'social_apps': check_social_apps(),
        'categories': check_categories(),
        'books': check_books(),
        'environment': check_environment(),
        'security': check_security(),
    }

    # Contar erros e avisos
    errors = sum(1 for r in results.values() if r.get('status') == 'error')
    warnings = sum(1 for r in results.values() if r.get('status') == 'warning')

    context = {
        'results': results,
        'errors_count': errors,
        'warnings_count': warnings,
        'all_ok': errors == 0 and warnings == 0,
    }

    return render(request, 'admin_tools/health_check.html', context)


@staff_member_required
def quick_stats_json(request):
    """Retorna estatísticas rápidas em JSON para dashboard."""
    stats = {
        'database_ok': check_database_connection(),
        'site_configured': Site.objects.filter(id=1).exists(),
        'categories': Category.objects.count(),
        'books': Book.objects.count(),
        'social_apps': SocialApp.objects.count(),
        'debug_mode': settings.DEBUG,
    }
    return JsonResponse(stats)


# ===== HELPER FUNCTIONS =====

def check_database_connection():
    """Verifica se o banco está conectado."""
    try:
        connection.cursor()
        return True
    except Exception:
        return False


def check_database():
    """Verifica status do banco de dados."""
    try:
        connection.cursor()
        db_settings = settings.DATABASES['default']
        engine = db_settings['ENGINE'].split('.')[-1]

        return {
            'status': 'success',
            'message': f'Conectado ({engine})',
            'details': f"Engine: {engine}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Erro de conexão',
            'details': str(e)
        }


def check_redis():
    """Verifica status do Redis."""
    try:
        from django.core.cache import cache
        cache.set('health_check_test', 'OK', 10)
        result = cache.get('health_check_test')

        if result == 'OK':
            cache.delete('health_check_test')
            return {
                'status': 'success',
                'message': 'Redis conectado',
                'details': 'Cache funcionando corretamente'
            }
        else:
            return {
                'status': 'warning',
                'message': 'Redis com problemas',
                'details': 'Cache respondeu incorretamente'
            }
    except Exception as e:
        return {
            'status': 'warning',
            'message': 'Redis não disponível',
            'details': 'Cache em banco ativo (fallback)'
        }


def check_site():
    """Verifica configuração do Site."""
    try:
        site = Site.objects.get(id=1)
        return {
            'status': 'success',
            'message': f'Site configurado: {site.name}',
            'details': f'Domain: {site.domain}'
        }
    except Site.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Site não configurado',
            'details': 'Execute setup_initial_data'
        }


def check_social_apps():
    """Verifica apps sociais."""
    apps = SocialApp.objects.all()

    if apps.exists():
        configured = [app.name for app in apps if app.client_id and app.secret]
        incomplete = [app.name for app in apps if not (app.client_id and app.secret)]

        if incomplete:
            return {
                'status': 'warning',
                'message': f'{len(configured)} configurados, {len(incomplete)} incompletos',
                'details': f'OK: {", ".join(configured) or "Nenhum"} | Incompleto: {", ".join(incomplete)}'
            }
        else:
            return {
                'status': 'success',
                'message': f'{len(configured)} apps configurados',
                'details': f'{", ".join(configured)}'
            }
    else:
        return {
            'status': 'warning',
            'message': 'Nenhum app social configurado',
            'details': 'Execute setup_initial_data'
        }


def check_categories():
    """Verifica categorias."""
    count = Category.objects.count()
    featured = Category.objects.filter(featured=True).count()

    if count > 0:
        return {
            'status': 'success',
            'message': f'{count} categorias cadastradas',
            'details': f'{featured} em destaque'
        }
    else:
        return {
            'status': 'warning',
            'message': 'Nenhuma categoria cadastrada',
            'details': 'Execute setup_initial_data'
        }


def check_books():
    """Verifica livros."""
    count = Book.objects.count()

    if count > 0:
        return {
            'status': 'success',
            'message': f'{count} livros cadastrados',
            'details': 'Banco populado'
        }
    else:
        return {
            'status': 'warning',
            'message': 'Nenhum livro cadastrado',
            'details': 'Execute setup_initial_data ou adicione via admin'
        }


def check_environment():
    """Verifica variáveis de ambiente importantes."""
    import os

    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        return {
            'status': 'error',
            'message': f'{len(missing)} variáveis faltando',
            'details': f'Faltam: {", ".join(missing)}'
        }
    else:
        return {
            'status': 'success',
            'message': 'Variáveis essenciais OK',
            'details': 'SECRET_KEY, DATABASE_URL configurados'
        }


def check_security():
    """Verifica configurações de segurança."""
    issues = []

    if settings.DEBUG:
        issues.append('DEBUG=True em produção')

    if '*' in settings.ALLOWED_HOSTS:
        issues.append('ALLOWED_HOSTS permite todos (*)')

    if issues:
        return {
            'status': 'error',
            'message': f'{len(issues)} problemas de segurança',
            'details': ' | '.join(issues)
        }
    else:
        return {
            'status': 'success',
            'message': 'Configurações de segurança OK',
            'details': 'DEBUG=False, ALLOWED_HOSTS restrito'
        }


# ===== BOOK SEARCH AND ASSOCIATION FOR AUTHOR ADMIN =====

@staff_member_required
def book_search_view(request):
    """
    API para buscar livros por título.
    Usado no admin de autores para associar livros existentes.
    """
    query = request.GET.get('q', '').strip()
    exclude_author_id = request.GET.get('exclude_author', None)
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Buscar livros pelo título
    books = Book.objects.filter(title__icontains=query).order_by('title')[:20]
    
    # Excluir livros que já pertencem ao autor sendo editado
    if exclude_author_id:
        try:
            exclude_author_id = int(exclude_author_id)
            books = books.exclude(author_id=exclude_author_id)
        except (ValueError, TypeError):
            pass
    
    results = []
    for book in books:
        results.append({
            'id': book.pk,
            'title': book.title,
            'author': book.author.name if book.author else None,
            'isbn': book.isbn or '',
        })
    
    return JsonResponse({'results': results})


@staff_member_required
@require_http_methods(["POST"])
def associate_book_view(request):
    """
    API para associar um livro a um autor.
    Recebe book_id e author_id via JSON.
    """
    import json
    
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        author_id = data.get('author_id')
        
        if not book_id or not author_id:
            return JsonResponse({'success': False, 'error': 'IDs não fornecidos'})
        
        book = Book.objects.get(pk=book_id)
        author = Author.objects.get(pk=author_id)
        
        # Associar o livro ao autor
        book.author = author
        book.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Livro "{book.title}" associado ao autor "{author.name}"'
        })
        
    except Book.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Livro não encontrado'})
    except Author.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Autor não encontrado'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

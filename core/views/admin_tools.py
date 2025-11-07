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
from core.models import Category, Book
from allauth.socialaccount.models import SocialApp
import io
import sys


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

"""
Views administrativas para executar comandos sem acesso ao Shell.
Útil para plano free do Render que não tem Shell access.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.db import connection
from django.contrib.sites.models import Site
from django.conf import settings
from core.models import Category, Book, Author
from core.models.author_work import AuthorWork
from allauth.socialaccount.models import SocialApp
import io
import sys
import csv


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


# ===== IMPORTAÇÃO CSV DE OBRAS LANÇADAS =====

@staff_member_required
def author_works_csv_template(request):
    """
    Retorna um arquivo CSV modelo para o usuário preencher
    e importar obras lançadas em lote.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="obras_lancadas_modelo.csv"'
    # BOM para Excel reconhecer UTF-8 corretamente
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['order', 'year', 'title', 'format', 'publisher', 'notes'])
    # Linhas de exemplo
    writer.writerow([1, '2022', 'Meu Primeiro Livro', 'Capa comum', 'CG.BookStore', ''])
    writer.writerow([2, '2023', 'Segundo Livro', 'E-book', 'Amazon BR', 'Edição revisada'])
    writer.writerow([3, '2024', 'Terceiro Livro', 'HQ', '', ''])

    return response


@staff_member_required
@require_http_methods(["POST"])
def import_author_works_view(request, author_id):
    """
    Processa o upload de um CSV com obras lançadas e as salva em lote
    para o autor indicado por author_id.

    Colunas esperadas: order, year, title, format, publisher, notes
    Colunas obrigatórias: year, title
    """
    try:
        author = Author.objects.get(pk=author_id)
    except Author.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Autor não encontrado.'})

    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado.'})

    # Validar extensão
    if not csv_file.name.lower().endswith('.csv'):
        return JsonResponse({'success': False, 'error': 'O arquivo deve ter extensão .csv'})

    # Ler e decodificar
    try:
        raw = csv_file.read()
        # Suporte a UTF-8 com ou sem BOM
        try:
            content = raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            content = raw.decode('latin-1')
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro ao ler o arquivo: {str(e)}'})

    # Detectar o delimitador automaticamente
    lines = content.splitlines()
    first_line = lines[0] if lines else ''
    
    delimiter = ','
    if first_line:
        candidates = [',', ';', '\t']
        best_cand = ','
        max_non_empty = 0
        for cand in candidates:
            parts = first_line.split(cand)
            non_empty_count = sum(1 for p in parts if p.strip())
            if non_empty_count > max_non_empty:
                max_non_empty = non_empty_count
                best_cand = cand
        delimiter = best_cand

    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

    # Validar cabeçalho
    if not reader.fieldnames:
        return JsonResponse({'success': False, 'error': 'Arquivo CSV vazio ou sem cabeçalho.'})

    import unicodedata
    def normalize_header(h):
        if not h:
            return ''
        s = h.strip()
        # Remover acentos
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        s = s.lower()
        if s in ('titulo', 'title'):
            return 'title'
        if s in ('ordem', 'order'):
            return 'order'
        if s.startswith('ano'):
            return 'year'
        if s in ('formato', 'format'):
            return 'format'
        if any(s.startswith(x) for x in ('editora', 'publisher', 'loja')):
            return 'publisher'
        if any(s.startswith(x) for x in ('obs', 'notes', 'nota')):
            return 'notes'
        return s

    # Mapear chaves originais do CSV para chaves normalizadas
    normalized_fieldnames = {f: normalize_header(f) for f in reader.fieldnames if f}
    fieldnames_normalized = set(normalized_fieldnames.values())

    required_columns = {'year', 'title'}
    missing = required_columns - fieldnames_normalized
    if missing:
        return JsonResponse({
            'success': False,
            'error': f'Colunas obrigatórias ausentes: {", ".join(missing)}. '
                     f'O CSV deve conter pelo menos: Ano, Título (ou year, title)'
        })

    works_to_create = []
    errors = []
    LIMIT = 500

    for i, row in enumerate(reader, start=2):  # linha 2 = primeira linha de dados
        if len(works_to_create) >= LIMIT:
            errors.append(f'Limite de {LIMIT} obras por importação atingido. Linhas restantes ignoradas.')
            break

        # Normalizar chaves do row para as chaves normalizadas mapeadas
        row_norm = {}
        for k, v in row.items():
            if k and k in normalized_fieldnames:
                row_norm[normalized_fieldnames[k]] = (v or '').strip()

        title = row_norm.get('title', '').strip()
        year = row_norm.get('year', '').strip()

        # Ignorar linhas sem título
        if not title:
            continue

        if not year:
            errors.append(f'Linha {i}: campo "year" vazio — obra "{title}" ignorada.')
            continue

        # order: padrão 0 se inválido
        try:
            order = int(row.get('order', 0) or 0)
        except (ValueError, TypeError):
            order = 0

        work_format = row.get('format', 'Capa comum').strip() or 'Capa comum'
        publisher = row.get('publisher', '').strip()
        notes = row.get('notes', '').strip()

        works_to_create.append(AuthorWork(
            author=author,
            order=order,
            year=year,
            title=title,
            format=work_format,
            publisher=publisher,
            notes=notes,
        ))

    if not works_to_create and not errors:
        return JsonResponse({'success': False, 'error': 'Nenhuma obra válida encontrada no arquivo.'})

    if works_to_create:
        AuthorWork.objects.bulk_create(works_to_create)

    return JsonResponse({
        'success': True,
        'imported': len(works_to_create),
        'errors': errors,
        'message': (
            f'{len(works_to_create)} obra(s) importada(s) com sucesso!'
            + (f' {len(errors)} aviso(s).' if errors else '')
        ),
    })

@csrf_exempt
@require_POST
def delete_author_works_view(request, author_id):
    """
    Deleta todas as obras cadastradas de um autor específico.
    Apenas para uso de administradores autenticados.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Acesso negado.'}, status=403)

    try:
        author = Author.objects.get(pk=author_id)
        works_count = author.works.count()
        if works_count == 0:
            return JsonResponse({'success': False, 'error': 'Nenhuma obra para excluir.'})
        
        author.works.all().delete()
        return JsonResponse({
            'success': True,
            'message': f'{works_count} obra(s) excluída(s) com sucesso!'
        })
    except Author.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Autor não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

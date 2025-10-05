"""
Views AJAX para gerenciamento da Biblioteca Pessoal.
Permite adicionar/remover livros, criar prateleiras personalizadas.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.models import Book
from accounts.models import BookShelf
import json


@login_required
@require_http_methods(["POST"])
def add_to_shelf(request):
    """
    Adiciona um livro a uma prateleira do usuário.

    Parâmetros POST:
    - book_id (int): ID do livro
    - shelf_type (str): Tipo de prateleira (favorites, to_read, reading, read, abandoned, custom)
    - custom_shelf_name (str, opcional): Nome da prateleira personalizada
    - notes (str, opcional): Notas pessoais sobre o livro

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - shelf_counts (dict): Contadores atualizados de cada prateleira
    """
    try:
        # Parse JSON do body
        data = json.loads(request.body)

        book_id = data.get('book_id')
        shelf_type = data.get('shelf_type', 'to_read')
        custom_shelf_name = data.get('custom_shelf_name', '').strip()
        notes = data.get('notes', '').strip()

        # Validações
        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        # Buscar livro
        book = get_object_or_404(Book, id=book_id)

        # Validar shelf_type
        valid_shelf_types = ['favorites', 'to_read', 'reading', 'read', 'abandoned', 'custom']
        if shelf_type not in valid_shelf_types:
            return JsonResponse({
                'success': False,
                'message': f'Tipo de prateleira inválido: {shelf_type}'
            }, status=400)

        # Se for custom, validar nome
        if shelf_type == 'custom':
            if not custom_shelf_name:
                return JsonResponse({
                    'success': False,
                    'message': 'Nome da prateleira personalizada é obrigatório.'
                }, status=400)
            if len(custom_shelf_name) > 100:
                return JsonResponse({
                    'success': False,
                    'message': 'Nome da prateleira muito longo (máx: 100 caracteres).'
                }, status=400)

        # Verificar se já existe na mesma prateleira
        existing = BookShelf.objects.filter(
            user=request.user,
            book=book,
            shelf_type=shelf_type,
            custom_shelf_name=custom_shelf_name if shelf_type == 'custom' else ''
        ).first()

        if existing:
            shelf_display = existing.get_shelf_display()
            return JsonResponse({
                'success': False,
                'message': f'"{book.title}" já está em "{shelf_display}".'
            }, status=400)

        # Criar entrada na prateleira
        bookshelf = BookShelf.objects.create(
            user=request.user,
            book=book,
            shelf_type=shelf_type,
            custom_shelf_name=custom_shelf_name if shelf_type == 'custom' else '',
            notes=notes
        )

        # Calcular contadores atualizados
        shelf_counts = {
            'favorites': BookShelf.objects.filter(user=request.user, shelf_type='favorites').count(),
            'to_read': BookShelf.objects.filter(user=request.user, shelf_type='to_read').count(),
            'reading': BookShelf.objects.filter(user=request.user, shelf_type='reading').count(),
            'read': BookShelf.objects.filter(user=request.user, shelf_type='read').count(),
            'abandoned': BookShelf.objects.filter(user=request.user, shelf_type='abandoned').count(),
        }

        shelf_display = bookshelf.get_shelf_display()

        return JsonResponse({
            'success': True,
            'message': f'"{book.title}" adicionado a "{shelf_display}"!',
            'shelf_counts': shelf_counts,
            'bookshelf_id': bookshelf.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao adicionar livro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def remove_from_shelf(request):
    """
    Remove um livro de uma prateleira do usuário.

    Parâmetros POST:
    - bookshelf_id (int): ID do BookShelf a ser removido

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - shelf_counts (dict): Contadores atualizados
    """
    try:
        data = json.loads(request.body)
        bookshelf_id = data.get('bookshelf_id')

        if not bookshelf_id:
            return JsonResponse({
                'success': False,
                'message': 'ID da prateleira não fornecido.'
            }, status=400)

        # Buscar e verificar ownership
        bookshelf = get_object_or_404(BookShelf, id=bookshelf_id, user=request.user)

        book_title = bookshelf.book.title
        shelf_display = bookshelf.get_shelf_display()

        # Deletar
        bookshelf.delete()

        # Calcular contadores atualizados
        shelf_counts = {
            'favorites': BookShelf.objects.filter(user=request.user, shelf_type='favorites').count(),
            'to_read': BookShelf.objects.filter(user=request.user, shelf_type='to_read').count(),
            'reading': BookShelf.objects.filter(user=request.user, shelf_type='reading').count(),
            'read': BookShelf.objects.filter(user=request.user, shelf_type='read').count(),
            'abandoned': BookShelf.objects.filter(user=request.user, shelf_type='abandoned').count(),
        }

        return JsonResponse({
            'success': True,
            'message': f'"{book_title}" removido de "{shelf_display}".',
            'shelf_counts': shelf_counts
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao remover livro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_book_shelves(request, book_id):
    """
    Retorna todas as prateleiras em que um livro está para o usuário atual.

    Parâmetros GET:
    - book_id (int): ID do livro (via URL)

    Retorna JSON:
    - success (bool)
    - shelves (list): Lista de prateleiras [{id, shelf_type, shelf_display, notes}]
    """
    try:
        book = get_object_or_404(Book, id=book_id)

        shelves = BookShelf.objects.filter(
            user=request.user,
            book=book
        ).values('id', 'shelf_type', 'custom_shelf_name', 'notes', 'date_added')

        shelves_list = []
        for shelf in shelves:
            shelf_display = shelf['custom_shelf_name'] if shelf['shelf_type'] == 'custom' else dict(
                BookShelf.SHELF_TYPES).get(shelf['shelf_type'])

            shelves_list.append({
                'id': shelf['id'],
                'shelf_type': shelf['shelf_type'],
                'shelf_display': shelf_display,
                'notes': shelf['notes'],
                'date_added': shelf['date_added'].strftime('%d/%m/%Y')
            })

        return JsonResponse({
            'success': True,
            'shelves': shelves_list,
            'book_title': book.title
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar prateleiras: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def create_custom_shelf(request):
    """
    Cria uma nova prateleira personalizada (sem adicionar livros ainda).
    Apenas valida o nome e retorna sucesso.

    Parâmetros POST:
    - custom_shelf_name (str): Nome da prateleira personalizada

    Retorna JSON:
    - success (bool)
    - message (str)
    - shelf_name (str): Nome validado
    """
    try:
        data = json.loads(request.body)
        custom_shelf_name = data.get('custom_shelf_name', '').strip()

        # Validações
        if not custom_shelf_name:
            return JsonResponse({
                'success': False,
                'message': 'Nome da prateleira não pode ser vazio.'
            }, status=400)

        if len(custom_shelf_name) > 100:
            return JsonResponse({
                'success': False,
                'message': 'Nome muito longo (máx: 100 caracteres).'
            }, status=400)

        # Verificar se já existe uma prateleira com esse nome
        existing = BookShelf.objects.filter(
            user=request.user,
            shelf_type='custom',
            custom_shelf_name=custom_shelf_name
        ).exists()

        if existing:
            return JsonResponse({
                'success': False,
                'message': f'Você já tem uma prateleira chamada "{custom_shelf_name}".'
            }, status=400)

        return JsonResponse({
            'success': True,
            'message': f'Prateleira "{custom_shelf_name}" validada! Adicione livros a ela.',
            'shelf_name': custom_shelf_name
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao criar prateleira: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def move_to_shelf(request):
    """
    Move um livro de uma prateleira para outra.

    Parâmetros POST:
    - bookshelf_id (int): ID do BookShelf atual
    - new_shelf_type (str): Novo tipo de prateleira
    - new_custom_shelf_name (str, opcional): Nome da nova prateleira personalizada

    Retorna JSON:
    - success (bool)
    - message (str)
    - shelf_counts (dict): Contadores atualizados
    """
    try:
        data = json.loads(request.body)
        bookshelf_id = data.get('bookshelf_id')
        new_shelf_type = data.get('new_shelf_type')
        new_custom_shelf_name = data.get('new_custom_shelf_name', '').strip()

        # Validações
        if not bookshelf_id or not new_shelf_type:
            return JsonResponse({
                'success': False,
                'message': 'Parâmetros incompletos.'
            }, status=400)

        # Buscar bookshelf existente
        bookshelf = get_object_or_404(BookShelf, id=bookshelf_id, user=request.user)

        # Validar novo shelf_type
        valid_shelf_types = ['favorites', 'to_read', 'reading', 'read', 'abandoned', 'custom']
        if new_shelf_type not in valid_shelf_types:
            return JsonResponse({
                'success': False,
                'message': f'Tipo de prateleira inválido: {new_shelf_type}'
            }, status=400)

        # Se for custom, validar nome
        if new_shelf_type == 'custom' and not new_custom_shelf_name:
            return JsonResponse({
                'success': False,
                'message': 'Nome da prateleira personalizada é obrigatório.'
            }, status=400)

        # Verificar se já existe na prateleira de destino
        existing = BookShelf.objects.filter(
            user=request.user,
            book=bookshelf.book,
            shelf_type=new_shelf_type,
            custom_shelf_name=new_custom_shelf_name if new_shelf_type == 'custom' else ''
        ).exclude(id=bookshelf_id).first()

        if existing:
            new_shelf_display = existing.get_shelf_display()
            return JsonResponse({
                'success': False,
                'message': f'O livro já está em "{new_shelf_display}".'
            }, status=400)

        old_shelf_display = bookshelf.get_shelf_display()

        # Atualizar prateleira
        bookshelf.shelf_type = new_shelf_type
        bookshelf.custom_shelf_name = new_custom_shelf_name if new_shelf_type == 'custom' else ''
        bookshelf.save()

        new_shelf_display = bookshelf.get_shelf_display()

        # Calcular contadores atualizados
        shelf_counts = {
            'favorites': BookShelf.objects.filter(user=request.user, shelf_type='favorites').count(),
            'to_read': BookShelf.objects.filter(user=request.user, shelf_type='to_read').count(),
            'reading': BookShelf.objects.filter(user=request.user, shelf_type='reading').count(),
            'read': BookShelf.objects.filter(user=request.user, shelf_type='read').count(),
            'abandoned': BookShelf.objects.filter(user=request.user, shelf_type='abandoned').count(),
        }

        return JsonResponse({
            'success': True,
            'message': f'Livro movido de "{old_shelf_display}" para "{new_shelf_display}".',
            'shelf_counts': shelf_counts
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao mover livro: {str(e)}'
        }, status=500)
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
    Se a prateleira personalizada não existir no perfil do usuário, ela é criada.
    """

    # ==========================================================
    #             INÍCIO DO BLOCO DE DEPURAÇÃO
    # ==========================================================
    print("--- [DEBUG] INICIANDO add_to_shelf ---")
    try:
        body_unicode = request.body.decode('utf-8')
        print(f"--- [DEBUG] Corpo da requisição (raw): {body_unicode}")
        data = json.loads(request.body)
        print(f"--- [DEBUG] Dados JSON parseados: {data}")
    except Exception as e:
        print(f"--- [DEBUG] ERRO AO PARSEAR JSON: {e}")
        return JsonResponse({'success': False, 'message': 'Erro de formato JSON.'}, status=400)

    book_id = data.get('book_id')
    shelf_type = data.get('shelf_type')
    custom_shelf_name = data.get('custom_shelf_name', '').strip()

    print(f"--- [DEBUG] Book ID recebido: {book_id} (Tipo: {type(book_id)})")
    print(f"--- [DEBUG] Shelf Type recebido: {shelf_type} (Tipo: {type(shelf_type)})")
    print(f"--- [DEBUG] Custom Shelf Name recebido: '{custom_shelf_name}' (Tipo: {type(custom_shelf_name)})")
    # ==========================================================
    #              FIM DO BLOCO DE DEPURAÇÃO
    # ==========================================================

    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        shelf_type = data.get('shelf_type', 'to_read')
        custom_shelf_name = data.get('custom_shelf_name', '').strip()
        notes = data.get('notes', '').strip()

        if not book_id:
            print("--- [DEBUG] ERRO: Book ID não fornecido.")  # Adicione print de erro
            return JsonResponse({'success': False, 'message': 'ID do livro não fornecido.'}, status=400)

        book = get_object_or_404(Book, id=book_id)

        valid_shelf_types = ['favorites', 'to_read', 'reading', 'read', 'abandoned', 'custom']
        if shelf_type not in valid_shelf_types:
            return JsonResponse({'success': False, 'message': f'Tipo de prateleira inválido: {shelf_type}'}, status=400)

        if shelf_type == 'custom':
            if not custom_shelf_name:
                return JsonResponse({'success': False, 'message': 'Nome da prateleira personalizada é obrigatório.'},
                                    status=400)
            if len(custom_shelf_name) > 100:
                return JsonResponse(
                    {'success': False, 'message': 'Nome da prateleira muito longo (máx: 100 caracteres).'}, status=400)

            # =======================================================================
            #  NOVA LÓGICA CRUCIAL: GARANTIR QUE A PRATELEIRA EXISTA NO PERFIL
            # =======================================================================
            profile = request.user.profile
            if not profile.has_custom_shelf(custom_shelf_name):
                profile.add_custom_shelf(custom_shelf_name)
            # =======================================================================

        # A lógica para verificar se o livro já está na prateleira continua a mesma
        existing = BookShelf.objects.filter(
            user=request.user,
            book=book,
            shelf_type=shelf_type,
            custom_shelf_name=custom_shelf_name if shelf_type == 'custom' else ''
        ).first()

        if existing:
            shelf_display = existing.get_shelf_display()
            return JsonResponse({'success': False, 'message': f'"{book.title}" já está em "{shelf_display}".'},
                                status=400)

        # Criar a entrada na tabela BookShelf
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
    Cria uma nova prateleira personalizada e adiciona à lista do perfil.

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

        # Verificar se já existe no profile
        profile = request.user.profile

        if profile.has_custom_shelf(custom_shelf_name):
            return JsonResponse({
                'success': False,
                'message': f'Você já tem uma prateleira chamada "{custom_shelf_name}".'
            }, status=400)

        # Adicionar à lista do profile
        added = profile.add_custom_shelf(custom_shelf_name)

        if not added:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao criar prateleira. Tente novamente.'
            }, status=500)

        return JsonResponse({
            'success': True,
            'message': f'Prateleira "{custom_shelf_name}" criada com sucesso!',
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



@login_required
@require_http_methods(["POST"])
def delete_custom_shelf(request):
    """
    Deleta uma prateleira personalizada e todos os seus livros.

    Parâmetros POST:
    - shelf_name (str): Nome da prateleira a ser deletada

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - deleted_books_count (int): Quantidade de livros removidos
    """
    try:
        data = json.loads(request.body)
        shelf_name = data.get('shelf_name', '').strip()

        # Validações
        if not shelf_name:
            return JsonResponse({
                'success': False,
                'message': 'Nome da prateleira não fornecido.'
            }, status=400)

        # Verificar se existe no profile
        profile = request.user.profile

        if not profile.has_custom_shelf(shelf_name):
            return JsonResponse({
                'success': False,
                'message': f'Prateleira "{shelf_name}" não encontrada.'
            }, status=404)

        # Contar livros que serão removidos
        books_in_shelf = BookShelf.objects.filter(
            user=request.user,
            shelf_type='custom',
            custom_shelf_name=shelf_name
        )
        deleted_count = books_in_shelf.count()

        # Deletar todos os livros da prateleira
        books_in_shelf.delete()

        # Remover da lista do profile
        removed = profile.remove_custom_shelf(shelf_name)

        if not removed:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao remover prateleira do perfil.'
            }, status=500)

        return JsonResponse({
            'success': True,
            'message': f'Prateleira "{shelf_name}" deletada com sucesso!',
            'deleted_books_count': deleted_count
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao deletar prateleira: {str(e)}'
        }, status=500)



@login_required
@require_http_methods(["POST"])
def rename_custom_shelf(request):
    """
    Renomeia uma prateleira personalizada.

    Parâmetros POST:
    - old_name (str): Nome atual da prateleira
    - new_name (str): Novo nome da prateleira

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - old_name (str): Nome antigo
    - new_name (str): Nome novo
    """
    try:
        data = json.loads(request.body)
        old_name = data.get('old_name', '').strip()
        new_name = data.get('new_name', '').strip()

        # Validações
        if not old_name or not new_name:
            return JsonResponse({
                'success': False,
                'message': 'Nomes da prateleira não fornecidos.'
            }, status=400)

        if len(new_name) > 100:
            return JsonResponse({
                'success': False,
                'message': 'Nome muito longo (máx: 100 caracteres).'
            }, status=400)

        if old_name == new_name:
            return JsonResponse({
                'success': False,
                'message': 'O novo nome deve ser diferente do atual.'
            }, status=400)

        # Verificar se prateleira antiga existe
        profile = request.user.profile

        if not profile.has_custom_shelf(old_name):
            return JsonResponse({
                'success': False,
                'message': f'Prateleira "{old_name}" não encontrada.'
            }, status=404)

        # Verificar se novo nome já existe
        if profile.has_custom_shelf(new_name):
            return JsonResponse({
                'success': False,
                'message': f'Já existe uma prateleira chamada "{new_name}".'
            }, status=400)

        # Atualizar todos os BookShelf com o novo nome
        updated_count = BookShelf.objects.filter(
            user=request.user,
            shelf_type='custom',
            custom_shelf_name=old_name
        ).update(custom_shelf_name=new_name)

        # Atualizar lista no profile
        profile.remove_custom_shelf(old_name)
        profile.add_custom_shelf(new_name)

        return JsonResponse({
            'success': True,
            'message': f'Prateleira renomeada de "{old_name}" para "{new_name}"!',
            'old_name': old_name,
            'new_name': new_name,
            'books_updated': updated_count
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao renomear prateleira: {str(e)}'
        }, status=500)



@login_required
@require_http_methods(["POST"])
def update_book_notes(request):
    """
    Atualiza as notas pessoais de um livro na biblioteca.

    Parâmetros POST:
    - bookshelf_id (int): ID do BookShelf
    - notes (str): Novas notas (pode ser vazio)

    Retorna JSON:
    - success (bool): Se a operação foi bem-sucedida
    - message (str): Mensagem de feedback
    - notes (str): Notas atualizadas
    """
    try:
        data = json.loads(request.body)
        bookshelf_id = data.get('bookshelf_id')
        notes = data.get('notes', '').strip()

        # Validações
        if not bookshelf_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do BookShelf não fornecido.'
            }, status=400)

        # Buscar bookshelf e verificar ownership
        bookshelf = get_object_or_404(BookShelf, id=bookshelf_id, user=request.user)

        # Atualizar notas
        bookshelf.notes = notes
        bookshelf.save()

        book_title = bookshelf.book.title
        shelf_display = bookshelf.get_shelf_display()

        return JsonResponse({
            'success': True,
            'message': f'Notas atualizadas para "{book_title}" em "{shelf_display}"!',
            'notes': notes,
            'book_title': book_title
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar notas: {str(e)}'
        }, status=500)
"""
Views AJAX para gerenciamento de progresso de leitura, prazos e notificações.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from accounts.models import ReadingProgress, ReadingNotification, BookShelf, SystemNotification
from core.models import Book
from datetime import datetime, date
import json


@login_required
@require_http_methods(["POST"])
def update_reading_progress(request):
    """
    Atualiza o progresso de leitura (página atual).

    POST Parameters:
        book_id (int): ID do livro
        current_page (int): Página atual

    Returns:
        JSON: {
            'success': bool,
            'message': str,
            'progress': {
                'current_page': int,
                'total_pages': int,
                'percentage': float,
                'is_finished': bool,
                'xp_gained': int (se completou)
            }
        }
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        current_page = data.get('current_page')

        # Validações
        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        if current_page is None:
            return JsonResponse({
                'success': False,
                'message': 'Página atual não fornecida.'
            }, status=400)

        try:
            current_page = int(current_page)
            if current_page < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Página inválida.'
            }, status=400)

        # Buscar livro
        book = get_object_or_404(Book, id=book_id)

        # Buscar ou criar progresso
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'total_pages': book.page_count or 1,
                'current_page': 0
            }
        )

        # Atualizar progresso
        xp_before = request.user.profile.total_xp if hasattr(request.user, 'profile') else 0
        progress.update_progress(current_page)
        xp_after = request.user.profile.total_xp if hasattr(request.user, 'profile') else 0
        xp_gained = xp_after - xp_before

        # Preparar resposta
        response_data = {
            'success': True,
            'message': f'Progresso atualizado: {progress.percentage}%',
            'progress': {
                'current_page': progress.current_page,
                'total_pages': progress.total_pages,
                'percentage': progress.percentage,
                'is_finished': progress.is_finished,
                'deadline_status': progress.deadline_status_display if progress.deadline else None,
            }
        }

        # Se completou o livro
        if progress.is_finished and xp_gained > 0:
            response_data['message'] = f'🎉 Parabéns! Você completou "{book.title}" e ganhou {xp_gained} XP!'
            response_data['progress']['xp_gained'] = xp_gained

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar progresso: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def set_reading_deadline(request):
    """
    Define ou atualiza o prazo de leitura.

    POST Parameters:
        book_id (int): ID do livro
        deadline (str): Data do prazo (YYYY-MM-DD)

    Returns:
        JSON: {
            'success': bool,
            'message': str,
            'deadline': {
                'date': str,
                'days_until': int,
                'status': str
            }
        }
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        deadline_str = data.get('deadline')

        # Validações
        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        if not deadline_str:
            return JsonResponse({
                'success': False,
                'message': 'Data do prazo não fornecida.'
            }, status=400)

        # Parsear data
        try:
            deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de data inválido. Use YYYY-MM-DD.'
            }, status=400)

        # Validar data futura
        if deadline_date < date.today():
            return JsonResponse({
                'success': False,
                'message': 'O prazo deve ser uma data futura.'
            }, status=400)

        # Buscar livro
        book = get_object_or_404(Book, id=book_id)

        # Buscar progresso
        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=book
            )
        except ReadingProgress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Você precisa começar a ler este livro primeiro.'
            }, status=400)

        # Definir prazo
        success = progress.set_deadline(deadline_date)

        if not success:
            return JsonResponse({
                'success': False,
                'message': 'Não é possível definir prazo para livro finalizado ou abandonado.'
            }, status=400)

        # Criar notificação para o usuário sobre a alteração do prazo
        ReadingNotification.objects.create(
            user=request.user,
            reading_progress=progress,
            notification_type='deadline_set',
            message=f'Você definiu um novo prazo para terminar sua leitura: {deadline_date.strftime("%d/%m/%Y")}.'
        )

        return JsonResponse({
            'success': True,
            'message': f'Prazo definido para {deadline_date.strftime("%d/%m/%Y")}',
            'deadline': {
                'date': deadline_str,
                'days_until': progress.days_until_deadline,
                'status': progress.deadline_status_display
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao definir prazo: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def remove_reading_deadline(request):
    """
    Remove o prazo de leitura.

    POST Parameters:
        book_id (int): ID do livro

    Returns:
        JSON: {
            'success': bool,
            'message': str
        }
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        book = get_object_or_404(Book, id=book_id)

        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=book
            )
        except ReadingProgress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Progresso não encontrado.'
            }, status=404)

        progress.deadline = None
        progress.deadline_notified = False
        progress.save()

        return JsonResponse({
            'success': True,
            'message': 'Prazo removido com sucesso.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao remover prazo: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def abandon_book_manual(request):
    """
    Abandona um livro manualmente.

    POST Parameters:
        book_id (int): ID do livro

    Returns:
        JSON: {
            'success': bool,
            'message': str
        }
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        book = get_object_or_404(Book, id=book_id)

        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=book
            )
        except ReadingProgress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Progresso não encontrado.'
            }, status=404)

        if progress.is_finished:
            return JsonResponse({
                'success': False,
                'message': 'Não é possível abandonar um livro já finalizado.'
            }, status=400)

        if progress.is_abandoned:
            return JsonResponse({
                'success': False,
                'message': 'Este livro já está abandonado.'
            }, status=400)

        # Abandonar
        success = progress.mark_as_abandoned(auto=False)

        if success:
            return JsonResponse({
                'success': True,
                'message': f'"{book.title}" foi movido para a prateleira "Abandonados".'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao abandonar o livro.'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao abandonar livro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def restore_book(request):
    """
    Restaura um livro abandonado.

    POST Parameters:
        book_id (int): ID do livro

    Returns:
        JSON: {
            'success': bool,
            'message': str
        }
    """
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'ID do livro não fornecido.'
            }, status=400)

        book = get_object_or_404(Book, id=book_id)

        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=book
            )
        except ReadingProgress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Progresso não encontrado.'
            }, status=404)

        if not progress.is_abandoned:
            return JsonResponse({
                'success': False,
                'message': 'Este livro não está abandonado.'
            }, status=400)

        # Restaurar
        success = progress.restore_from_abandoned()

        if success:
            return JsonResponse({
                'success': True,
                'message': f'"{book.title}" foi restaurado para a prateleira "Lendo".'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao restaurar o livro.'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao restaurar livro: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_reading_stats(request, book_id):
    """
    Retorna estatísticas detalhadas de um progresso de leitura.

    Args:
        book_id (int): ID do livro

    Returns:
        JSON: {
            'success': bool,
            'stats': {
                'current_page': int,
                'total_pages': int,
                'percentage': float,
                'is_finished': bool,
                'reading_time_days': int,
                'pages_per_day': float,
                'estimated_finish_date': str,
                'deadline': str or null,
                'deadline_status': str,
                'days_until_deadline': int or null,
                'is_abandoned': bool
            }
        }
    """
    try:
        book = get_object_or_404(Book, id=book_id)

        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=book
            )
        except ReadingProgress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Progresso não encontrado.'
            }, status=404)

        stats = {
            'current_page': progress.current_page,
            'total_pages': progress.total_pages,
            'percentage': progress.percentage,
            'is_finished': progress.is_finished,
            'reading_time_days': progress.reading_time_days,
            'pages_per_day': progress.pages_per_day,
            'estimated_finish_date': progress.estimated_finish_date.strftime(
                '%Y-%m-%d') if progress.estimated_finish_date else None,
            'deadline': progress.deadline.strftime('%Y-%m-%d') if progress.deadline else None,
            'deadline_status': progress.deadline_status_display if progress.deadline else None,
            'days_until_deadline': progress.days_until_deadline,
            'is_abandoned': progress.is_abandoned,
        }

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter estatísticas: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request):
    """
    Marca uma notificação como lida.

    POST Parameters:
        notification_id (int): ID da notificação

    Returns:
        JSON: {
            'success': bool,
            'message': str,
            'unread_count': int
        }
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')

        if not notification_id:
            return JsonResponse({
                'success': False,
                'message': 'ID da notificação não fornecido.'
            }, status=400)

        try:
            notification = ReadingNotification.objects.get(
                id=notification_id,
                user=request.user
            )
        except ReadingNotification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Notificação não encontrada.'
            }, status=404)

        notification.mark_as_read()

        # Contar não lidas
        unread_count = ReadingNotification.get_unread_count(request.user)

        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida.',
            'unread_count': unread_count
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificação: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """
    Marca todas as notificações como lidas.

    Returns:
        JSON: {
            'success': bool,
            'message': str,
            'marked_count': int
        }
    """
    try:
        marked = ReadingNotification.mark_all_as_read(request.user)

        return JsonResponse({
            'success': True,
            'message': f'{marked} notificação(ões) marcada(s) como lida(s).',
            'marked_count': marked
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificações: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """
    Lista notificações do usuário de forma paginada.

    Query Parameters:
        page (int): Número da página a ser retornada (default: 1)
        unread_only (bool): Apenas não lidas (default: false)
    """
    try:
        page_number = int(request.GET.get('page', 1))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

        # Define o número de notificações por página
        NOTIFICATIONS_PER_PAGE = 10

        # Buscar todas as notificações
        all_notifications = ReadingNotification.objects.filter(
            user=request.user
        ).select_related('reading_progress', 'reading_progress__book').order_by('-created_at')

        if unread_only:
            all_notifications = all_notifications.filter(is_read=False)

        # Configurar o paginador
        paginator = Paginator(all_notifications, NOTIFICATIONS_PER_PAGE)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            # Se a página solicitada não existir, retorna uma lista vazia
            return JsonResponse({
                'success': True,
                'notifications': [],
                'has_next_page': False,
                'unread_count': ReadingNotification.get_unread_count(request.user)
            })

        # Serializar os dados da página atual
        notifications_data = []
        for notif in page_obj.object_list:
            notifications_data.append({
                'id': notif.id,
                'type': notif.notification_type,
                'type_display': notif.get_notification_type_display(),
                'book_title': notif.book_title,
                'message': notif.message,
                'icon_class': notif.icon_class,
                'priority': notif.priority,
                'is_read': notif.is_read,
                'formatted_time': notif.formatted_time,
                'created_at': notif.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'has_next_page': page_obj.has_next(),
            'unread_count': ReadingNotification.get_unread_count(request.user)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao listar notificações: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_selected_notifications(request):
    """
    Deleta notificações selecionadas pelo usuário.

    POST Parameters:
        notification_ids (list[int]): Lista de IDs das notificações a deletar

    Returns:
        JSON: {
            'success': bool,
            'message': str,
            'deleted_count': int,
            'unread_count': int
        }
    """
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])

        if not notification_ids or not isinstance(notification_ids, list):
            return JsonResponse({
                'success': False,
                'message': 'Lista de IDs não fornecida ou inválida.'
            }, status=400)

        # Validar que todos os IDs são inteiros
        try:
            notification_ids = [int(id) for id in notification_ids]
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'IDs de notificação inválidos.'
            }, status=400)

        # Buscar notificações do usuário atual
        notifications_to_delete = ReadingNotification.objects.filter(
            id__in=notification_ids,
            user=request.user
        )

        # Contar quantas serão deletadas
        deleted_count = notifications_to_delete.count()

        if deleted_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'Nenhuma notificação encontrada para deletar.'
            }, status=404)

        # Deletar as notificações
        notifications_to_delete.delete()

        # Contar notificações não lidas restantes
        unread_count = ReadingNotification.get_unread_count(request.user)

        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} notificação(ões) deletada(s) com sucesso.',
            'deleted_count': deleted_count,
            'unread_count': unread_count
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao deletar notificações: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_unread_notifications_count(request):
    """
    Retorna apenas a contagem de notificações não lidas.
    Endpoint leve para atualizar o badge sem carregar todas as notificações.

    Returns:
        JSON: {
            'success': bool,
            'unread_count': int
        }
    """
    try:
        unread_count = ReadingNotification.get_unread_count(request.user)

        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter contador: {str(e)}',
            'unread_count': 0
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_all_notifications_unified(request):
    """
    Lista TODAS as notificações do usuário (todos os tipos) de forma unificada.

    Query Parameters:
        page (int): Número da página
        unread_only (bool): Apenas não lidas
        notification_type (str): Filtro por tipo (opcional)
        category (str): Filtro por categoria: 'reading', 'system', 'all' (default: 'all')

    Returns:
        JSON com notificações de todos os tipos unificadas
    """
    try:
        page_number = int(request.GET.get('page', 1))
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
        category_filter = request.GET.get('category', 'all')

        NOTIFICATIONS_PER_PAGE = 10

        # Lista para acumular todas as notificações
        all_notifications = []

        # Buscar notificações de leitura
        if category_filter in ['all', 'reading']:
            reading_notifs = ReadingNotification.objects.filter(
                user=request.user
            ).select_related('reading_progress', 'reading_progress__book')

            if unread_only:
                reading_notifs = reading_notifs.filter(is_read=False)

            all_notifications.extend(reading_notifs)

        # Buscar notificações do sistema
        if category_filter in ['all', 'system']:
            system_notifs = SystemNotification.objects.filter(
                user=request.user
            )

            if unread_only:
                system_notifs = system_notifs.filter(is_read=False)

            all_notifications.extend(system_notifs)

        # Ordenar todas juntas por data de criação
        all_notifications.sort(key=lambda x: x.created_at, reverse=True)

        # Paginar
        paginator = Paginator(all_notifications, NOTIFICATIONS_PER_PAGE)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            return JsonResponse({
                'success': True,
                'notifications': [],
                'has_next_page': False,
                'unread_count': get_total_unread_count(request.user),
                'category_counts': get_category_counts(request.user)
            })

        # Serializar notificações
        notifications_data = []
        for notif in page_obj.object_list:
            # Determinar categoria
            if isinstance(notif, ReadingNotification):
                category = 'reading'
            elif isinstance(notif, SystemNotification):
                category = 'system'
            else:
                category = 'other'

            notifications_data.append({
                'id': notif.id,
                'category': category,
                'type': notif.notification_type,
                'type_display': notif.get_notification_type_display(),
                'book_title': notif.book_title,
                'message': notif.message,
                'icon_class': notif.icon_class,
                'priority': notif.priority,
                'priority_name': notif.priority_name,
                'is_read': notif.is_read,
                'formatted_time': notif.formatted_time,
                'created_at': notif.created_at.isoformat(),
                'action_url': notif.action_url,
                'action_text': notif.action_text,
            })

        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'has_next_page': page_obj.has_next(),
            'unread_count': get_total_unread_count(request.user),
            'category_counts': get_category_counts(request.user)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao listar notificações: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read_unified(request):
    """
    Marca uma notificação como lida (qualquer tipo).

    POST Parameters:
        notification_id (int): ID da notificação
        category (str): Categoria ('reading' ou 'system')

    Returns:
        JSON com sucesso e contadores atualizados
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        category = data.get('category', 'reading')

        if not notification_id:
            return JsonResponse({
                'success': False,
                'message': 'ID da notificação não fornecido.'
            }, status=400)

        # Buscar notificação pelo tipo
        notification = None
        if category == 'reading':
            try:
                notification = ReadingNotification.objects.get(
                    id=notification_id,
                    user=request.user
                )
            except ReadingNotification.DoesNotExist:
                pass
        elif category == 'system':
            try:
                notification = SystemNotification.objects.get(
                    id=notification_id,
                    user=request.user
                )
            except SystemNotification.DoesNotExist:
                pass

        if not notification:
            return JsonResponse({
                'success': False,
                'message': 'Notificação não encontrada.'
            }, status=404)

        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida.',
            'unread_count': get_total_unread_count(request.user),
            'category_counts': get_category_counts(request.user)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificação: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_selected_notifications_unified(request):
    """
    Deleta notificações selecionadas (qualquer tipo).

    POST Parameters:
        notifications (list): Lista de dicts com 'id' e 'category'
        Exemplo: [{'id': 1, 'category': 'reading'}, {'id': 2, 'category': 'system'}]

    Returns:
        JSON com sucesso e quantidade deletada
    """
    try:
        data = json.loads(request.body)
        notifications_to_delete = data.get('notifications', [])

        if not notifications_to_delete or not isinstance(notifications_to_delete, list):
            return JsonResponse({
                'success': False,
                'message': 'Lista de notificações não fornecida ou inválida.'
            }, status=400)

        deleted_count = 0

        for notif_data in notifications_to_delete:
            notif_id = notif_data.get('id')
            category = notif_data.get('category', 'reading')

            if not notif_id:
                continue

            # Deletar conforme o tipo
            if category == 'reading':
                deleted = ReadingNotification.objects.filter(
                    id=notif_id,
                    user=request.user
                ).delete()[0]
                deleted_count += deleted
            elif category == 'system':
                deleted = SystemNotification.objects.filter(
                    id=notif_id,
                    user=request.user
                ).delete()[0]
                deleted_count += deleted

        if deleted_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'Nenhuma notificação encontrada para deletar.'
            }, status=404)

        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} notificação(ões) deletada(s) com sucesso.',
            'deleted_count': deleted_count,
            'unread_count': get_total_unread_count(request.user),
            'category_counts': get_category_counts(request.user)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados JSON inválidos.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao deletar notificações: {str(e)}'
        }, status=500)


# ========== FUNÇÕES AUXILIARES ==========

def get_total_unread_count(user):
    """Retorna o total de notificações não lidas de TODOS os tipos."""
    reading_count = ReadingNotification.objects.filter(
        user=user,
        is_read=False
    ).count()

    system_count = SystemNotification.objects.filter(
        user=user,
        is_read=False
    ).count()

    return reading_count + system_count


def get_category_counts(user):
    """Retorna contadores por categoria."""
    return {
        'reading': {
            'total': ReadingNotification.objects.filter(user=user).count(),
            'unread': ReadingNotification.objects.filter(user=user, is_read=False).count()
        },
        'system': {
            'total': SystemNotification.objects.filter(user=user).count(),
            'unread': SystemNotification.objects.filter(user=user, is_read=False).count()
        }
    }

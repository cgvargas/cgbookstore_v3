"""
Views para download de manuscritos por editoras
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone

from new_authors.models import (
    AuthorBook,
    Chapter,
    PublisherProfile,
    PublisherSubscription,
    ManuscriptDownload
)
from new_authors.services.manuscript_generator import ManuscriptGenerator


def get_client_ip(request):
    """Obtém o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@require_http_methods(["GET"])
def download_chapter(request, book_id, chapter_id, file_format):
    """
    Download de um capítulo individual em PDF ou DOCX

    Args:
        book_id: ID do livro
        chapter_id: ID do capítulo
        file_format: 'pdf' ou 'docx'
    """
    # Validar formato
    if file_format not in ['pdf', 'docx']:
        raise Http404("Formato inválido")

    # Verificar se usuário é editora
    try:
        publisher = PublisherProfile.objects.get(user=request.user)
    except PublisherProfile.DoesNotExist:
        messages.error(request, "Apenas editoras podem baixar manuscritos.")
        return redirect('new_authors:book_list')

    # Verificar assinatura ativa
    try:
        subscription = PublisherSubscription.objects.get(publisher=publisher)
    except PublisherSubscription.DoesNotExist:
        messages.error(request, "Você precisa de uma assinatura ativa para baixar manuscritos.")
        return redirect('new_authors:publisher_plans')

    if not subscription.is_active():
        messages.error(request, "Sua assinatura expirou. Renove para continuar baixando manuscritos.")
        return redirect('new_authors:publisher_plans')

    # Verificar limite de downloads
    if not subscription.can_download_chapter():
        remaining = subscription.plan.max_chapter_downloads - subscription.chapter_downloads_this_month
        messages.error(
            request,
            f"Você atingiu o limite de downloads do mês ({subscription.plan.max_chapter_downloads}). "
            f"Faça upgrade do seu plano para downloads ilimitados."
        )
        return redirect('new_authors:publisher_dashboard')

    # Buscar livro e capítulo
    book = get_object_or_404(AuthorBook, id=book_id, status='published')
    chapter = get_object_or_404(Chapter, id=chapter_id, book=book, is_published=True)

    # Gerar documento
    generator = ManuscriptGenerator(book=book, publisher=publisher)

    try:
        if file_format == 'pdf':
            buffer = generator.generate_pdf(chapters=[chapter])
            content_type = 'application/pdf'
        else:  # docx
            buffer = generator.generate_docx(chapters=[chapter])
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        # Registrar download
        ManuscriptDownload.objects.create(
            publisher=publisher,
            book=book,
            chapter=chapter,
            download_type='chapter',
            file_format=file_format,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Incrementar contador
        subscription.increment_chapter_download()

        # Preparar response
        filename = generator.get_filename(file_format, chapter=chapter)
        response = HttpResponse(buffer.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        messages.error(request, f"Erro ao gerar documento: {str(e)}")
        return redirect('new_authors:book_detail', book_id=book_id)


@login_required
@require_http_methods(["GET"])
def download_full_book(request, book_id, file_format):
    """
    Download do livro completo em PDF ou DOCX

    Args:
        book_id: ID do livro
        file_format: 'pdf' ou 'docx'
    """
    # Validar formato
    if file_format not in ['pdf', 'docx']:
        raise Http404("Formato inválido")

    # Verificar se usuário é editora
    try:
        publisher = PublisherProfile.objects.get(user=request.user)
    except PublisherProfile.DoesNotExist:
        messages.error(request, "Apenas editoras podem baixar manuscritos.")
        return redirect('new_authors:book_list')

    # Verificar assinatura ativa
    try:
        subscription = PublisherSubscription.objects.get(publisher=publisher)
    except PublisherSubscription.DoesNotExist:
        messages.error(request, "Você precisa de uma assinatura ativa para baixar manuscritos.")
        return redirect('new_authors:publisher_plans')

    if not subscription.is_active():
        messages.error(request, "Sua assinatura expirou. Renove para continuar baixando manuscritos.")
        return redirect('new_authors:publisher_plans')

    # Verificar se o plano permite download de livro completo
    if not subscription.plan.can_download_full_book:
        messages.error(
            request,
            "Seu plano não permite download de livros completos. "
            "Faça upgrade para o plano Premium ou Enterprise."
        )
        return redirect('new_authors:publisher_plans')

    # Verificar limite de downloads (contar como múltiplos downloads)
    book = get_object_or_404(AuthorBook, id=book_id, status='published')
    total_chapters = book.chapters.filter(is_published=True).count()

    if subscription.plan.max_chapter_downloads is not None:
        if subscription.chapter_downloads_this_month + total_chapters > subscription.plan.max_chapter_downloads:
            messages.error(
                request,
                f"Você não tem downloads suficientes este mês para baixar o livro completo "
                f"({total_chapters} capítulos). Restam {subscription.plan.max_chapter_downloads - subscription.chapter_downloads_this_month} downloads."
            )
            return redirect('new_authors:publisher_dashboard')

    # Gerar documento
    generator = ManuscriptGenerator(book=book, publisher=publisher)

    try:
        if file_format == 'pdf':
            buffer = generator.generate_pdf(full_book=True)
            content_type = 'application/pdf'
        else:  # docx
            buffer = generator.generate_docx(full_book=True)
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        # Registrar download
        ManuscriptDownload.objects.create(
            publisher=publisher,
            book=book,
            chapter=None,
            download_type='full_book',
            file_format=file_format,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Incrementar contador (livro completo conta como múltiplos downloads)
        for _ in range(total_chapters):
            subscription.increment_chapter_download()

        # Preparar response
        filename = generator.get_filename(file_format)
        response = HttpResponse(buffer.getvalue(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        messages.success(
            request,
            f"Livro '{book.title}' baixado com sucesso! "
            f"({total_chapters} capítulos, {subscription.plan.max_chapter_downloads - subscription.chapter_downloads_this_month if subscription.plan.max_chapter_downloads else 'ilimitados'} downloads restantes)"
        )

        return response

    except Exception as e:
        messages.error(request, f"Erro ao gerar documento: {str(e)}")
        return redirect('new_authors:book_detail', book_id=book_id)


@login_required
@require_http_methods(["GET"])
def download_limits_info(request):
    """
    API endpoint para obter informações sobre limites de download

    Returns:
        JSON com informações de limites
    """
    try:
        publisher = PublisherProfile.objects.get(user=request.user)
        subscription = PublisherSubscription.objects.get(publisher=publisher)

        data = {
            'is_active': subscription.is_active(),
            'plan_name': subscription.plan.name,
            'can_download_full_book': subscription.plan.can_download_full_book,
            'max_manuscript_views': subscription.plan.max_manuscript_views,
            'max_chapter_downloads': subscription.plan.max_chapter_downloads,
            'manuscript_views_this_month': subscription.manuscript_views_this_month,
            'chapter_downloads_this_month': subscription.chapter_downloads_this_month,
            'remaining_views': (
                subscription.plan.max_manuscript_views - subscription.manuscript_views_this_month
                if subscription.plan.max_manuscript_views is not None
                else None
            ),
            'remaining_downloads': (
                subscription.plan.max_chapter_downloads - subscription.chapter_downloads_this_month
                if subscription.plan.max_chapter_downloads is not None
                else None
            ),
            'reset_date': subscription.reset_date.isoformat() if subscription.reset_date else None,
            'expiration_date': subscription.expiration_date.isoformat() if subscription.expiration_date else None
        }

        return JsonResponse(data)

    except (PublisherProfile.DoesNotExist, PublisherSubscription.DoesNotExist):
        return JsonResponse({'error': 'Assinatura não encontrada'}, status=404)


@login_required
@require_http_methods(["GET"])
def download_history(request):
    """
    Histórico de downloads da editora

    Returns:
        JSON com histórico de downloads
    """
    try:
        publisher = PublisherProfile.objects.get(user=request.user)

        downloads = ManuscriptDownload.objects.filter(
            publisher=publisher
        ).select_related('book', 'chapter').order_by('-downloaded_at')[:50]

        data = {
            'downloads': [
                {
                    'id': download.id,
                    'book_title': download.book.title,
                    'book_id': download.book.id,
                    'chapter_number': download.chapter.number if download.chapter else None,
                    'chapter_title': download.chapter.title if download.chapter else None,
                    'download_type': download.get_download_type_display(),
                    'file_format': download.file_format.upper(),
                    'downloaded_at': download.downloaded_at.isoformat()
                }
                for download in downloads
            ],
            'total_downloads': ManuscriptDownload.objects.filter(publisher=publisher).count()
        }

        return JsonResponse(data)

    except PublisherProfile.DoesNotExist:
        return JsonResponse({'error': 'Editora não encontrada'}, status=404)

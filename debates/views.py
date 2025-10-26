from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from .models import DebateTopic, DebatePost, DebateVote
from core.models import Book


def debates_list(request):
    """Lista todos os tópicos de debate"""
    topics = DebateTopic.objects.select_related('book', 'creator').annotate(
        last_post_count=Count('posts')
    ).order_by('-is_pinned', '-updated_at')

    # Filtro por livro
    book_id = request.GET.get('book')
    if book_id:
        topics = topics.filter(book_id=book_id)

    # Busca
    search = request.GET.get('q')
    if search:
        topics = topics.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(book__title__icontains=search)
        )

    context = {
        'topics': topics,
        'search_query': search or '',
    }
    return render(request, 'debates/list.html', context)


def topic_detail(request, slug):
    """Detalhes de um tópico + posts"""
    topic = get_object_or_404(
        DebateTopic.objects.select_related('book', 'creator'),
        slug=slug
    )

    # Incrementar visualizações
    topic.increment_views()

    # Consulta simplificada para carregar todos os posts não deletados.
    # Removemos o filtro parent__isnull=True para incluir todos os posts do tópico.
    posts = topic.posts.exclude(is_deleted=True).select_related('author').prefetch_related('replies', 'votes').order_by('created_at')

    # A lógica de 'is_author' foi movida para o template.
    # Apenas adicionamos informações de voto.
    for post in posts:
        if request.user.is_authenticated:
            post.user_vote = post.get_user_vote(request.user)
        else:
            post.user_vote = None

    context = {
        'topic': topic,
        'posts': posts,
    }
    return render(request, 'debates/detail.html', context)


@login_required
def create_topic(request, book_id):
    """Criar novo tópico de debate"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title or not description:
            messages.error(request, 'Título e descrição são obrigatórios.')
            return redirect('core:book_detail', pk=book_id)

        topic = DebateTopic.objects.create(
            book=book,
            creator=request.user,
            title=title,
            description=description
        )

        messages.success(request, 'Tópico criado com sucesso!')
        return redirect('debates:topic_detail', slug=topic.slug)

    context = {'book': book}
    return render(request, 'debates/create.html', context)


@login_required
@require_POST
def create_post(request, topic_slug):
    """Criar post em um tópico"""
    topic = get_object_or_404(DebateTopic, slug=topic_slug)

    if topic.is_locked:
        return JsonResponse({'success': False, 'error': 'Tópico bloqueado'}, status=403)

    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        return JsonResponse({'success': False, 'error': 'Conteúdo obrigatório'}, status=400)

    parent = None
    if parent_id:
        parent = get_object_or_404(DebatePost, id=parent_id, topic=topic)

    post = DebatePost.objects.create(
        topic=topic,
        author=request.user,
        parent=parent,
        content=content
    )

    # Atualizar contador
    topic.update_posts_count()

    return JsonResponse({
        'success': True,
        'post_id': post.id,
        'message': 'Post criado com sucesso!'
    })


@login_required
@require_POST
def vote_post(request, post_id):
    """Votar em um post"""
    post = get_object_or_404(DebatePost, id=post_id)
    vote_type = request.POST.get('vote_type')

    if vote_type not in ['up', 'down']:
        return JsonResponse({'success': False, 'error': 'Tipo de voto inválido'}, status=400)

    # Verificar voto existente
    vote, created = DebateVote.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={'vote_type': vote_type}
    )

    if not created:
        if vote.vote_type == vote_type:
            # Remover voto
            vote.delete()
            action = 'removed'
        else:
            # Trocar voto
            vote.vote_type = vote_type
            vote.save()
            action = 'changed'
    else:
        action = 'created'

    # Atualizar score
    post.update_votes_score()

    return JsonResponse({
        'success': True,
        'action': action,
        'score': post.votes_score,
        'user_vote': post.get_user_vote(request.user)
    })


@login_required
@require_POST
def edit_post(request, post_id):
    """Editar post"""
    post = get_object_or_404(DebatePost, id=post_id)

    # Apenas autor pode editar
    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)

    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'success': False, 'error': 'Conteúdo obrigatório'}, status=400)

    from django.utils import timezone
    post.content = content
    post.edited_at = timezone.now()
    post.save()

    return JsonResponse({
        'success': True,
        'content': content,
        'edited_at': post.edited_at.strftime('%d/%m/%Y %H:%M')
    })


@login_required
@require_POST
def delete_post(request, post_id):
    """Deletar post (soft delete)"""
    post = get_object_or_404(DebatePost, id=post_id)

    # Apenas autor ou staff pode deletar
    if post.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)

    post.is_deleted = True
    post.save()

    # Atualizar contador
    post.topic.update_posts_count()

    return JsonResponse({'success': True, 'message': 'Post deletado'})
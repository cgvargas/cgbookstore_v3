from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Count
from core.models import Book
from accounts.models import BookReview, ReviewLike
from accounts.forms import BookReviewForm

@login_required
@require_POST
def save_book_review(request, book_id):
    """
    Salva ou atualiza a resenha de um livro submetida por AJAX.
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Busca resenha existente do usuário (se houver)
    review_instance = BookReview.objects.filter(book=book, user=request.user).first()
    
    form = BookReviewForm(request.POST, instance=review_instance)
    
    if form.is_valid():
        review = form.save(commit=False)
        review.book = book
        review.user = request.user
        review.is_public = True  # Marca automaticamente como pública para a comunidade
        review.save()
        
        # Opcional: Atualizar alguma estatística do User ou Book aqui.
        # O método .save() no model de BookReview (já criado) atualiza XP do usuário.

        return JsonResponse({
            'success': True,
            'message': 'Sua avaliação foi salva com sucesso!',
            'rating': review.rating,
        })
    else:
        # Extrai os erros
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({
            'success': False,
            'message': 'Houve um erro no preenchimento do formulário.',
            'errors': errors
        }, status=400)


@login_required
@require_POST
def delete_book_review(request, review_id):
    """
    Exclui a resenha (se pertencer ao usuário logado).
    """
    review = get_object_or_404(BookReview, id=review_id, user=request.user)
    review.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def toggle_review_like(request, review_id):
    """
    Alterna curtida de um usuário em uma resenha específica.
    """
    review = get_object_or_404(BookReview, id=review_id)
    like_obj, created = ReviewLike.objects.get_or_create(user=request.user, review=review)

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    likes_count = review.likes.count()

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': likes_count
    })


class BookReviewListView(ListView):
    """
    Página exclusiva para listar todas as opiniões/resenhas da comunidade sobre um livro.
    Reaproveita o contexto de BookDetailView parcialmente.
    """
    model = BookReview
    template_name = 'core/book_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        self.book = get_object_or_404(Book, id=self.kwargs['book_id'])
        qs = BookReview.objects.filter(book=self.book, is_public=True).select_related(
            'user', 'user__profile'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        ).order_by('-created_at')
        
        # Exclui a resenha do próprio usuário logado para não duplicar
        # (ela já aparece no card "Sua Avaliação Atual" no topo)
        if self.request.user.is_authenticated:
            qs = qs.exclude(user=self.request.user)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.book
        
        # Resenha do próprio usuário em evidência no topo local, se logado
        if self.request.user.is_authenticated:
            context['user_review'] = BookReview.objects.filter(
                book=self.book, user=self.request.user
            ).annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True)
            ).first()
        else:
            context['user_review'] = None
            
        return context


@login_required
@require_POST
def add_review_comment(request, review_id):
    """
    Adiciona um comentário a uma resenha via AJAX.
    """
    review = get_object_or_404(BookReview, id=review_id)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'success': False, 'error': 'O comentário não pode estar vazio.'}, status=400)

    if len(content) > 1000:
        return JsonResponse({'success': False, 'error': 'Comentário muito longo (máx. 1000 caracteres).'}, status=400)

    from accounts.models import ReviewComment
    comment = ReviewComment.objects.create(
        review=review,
        user=request.user,
        content=content,
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': request.user.first_name or request.user.username,
            'created_at': comment.created_at.strftime('%d %b %Y'),
        },
        'comments_count': review.comments.filter(is_active=True).count(),
    })


def get_review_comments(request, review_id):
    """
    Retorna os comentários de uma resenha via AJAX (GET).
    """
    review = get_object_or_404(BookReview, id=review_id)
    comments = review.comments.filter(is_active=True).select_related('user').order_by('created_at')

    is_review_owner = request.user.is_authenticated and review.user == request.user

    data = [
        {
            'id': c.id,
            'content': c.content,
            'author': c.user.first_name or c.user.username,
            # Pode excluir se for o autor do comentário OU o dono da resenha (moderação)
            'can_delete': request.user.is_authenticated and (
                c.user == request.user or is_review_owner
            ),
            'created_at': c.created_at.strftime('%d %b %Y'),
        }
        for c in comments
    ]

    return JsonResponse({'success': True, 'comments': data})


@login_required
@require_POST
def delete_review_comment(request, comment_id):
    """
    Deleta um comentário.
    Permitido para: autor do comentário OU autor da resenha (moderação).
    """
    from accounts.models import ReviewComment
    comment = get_object_or_404(ReviewComment, id=comment_id)

    # Verifica permissão: autor do comentário ou dono da resenha
    is_comment_author = comment.user == request.user
    is_review_owner = comment.review.user == request.user

    if not (is_comment_author or is_review_owner):
        return JsonResponse({'success': False, 'error': 'Sem permissão para excluir este comentário.'}, status=403)

    review_id = comment.review_id
    comment.delete()

    from accounts.models import BookReview as BR
    comments_count = BR.objects.get(id=review_id).comments.filter(is_active=True).count()

    return JsonResponse({'success': True, 'comments_count': comments_count})

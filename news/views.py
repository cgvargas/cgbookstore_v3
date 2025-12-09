from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Article, Category, Tag, Quiz, QuizQuestion, Newsletter, QuizAttempt


def news_home(request):
    """Página principal do jornal/notícias - estilo grade de jornal"""

    # Breaking news / Última hora
    breaking_news = Article.objects.filter(
        is_published=True,
        is_breaking=True
    ).order_by('-published_at').first()

    # Artigo em destaque principal (prioridade 5)
    featured_main = Article.objects.filter(
        is_published=True,
        is_featured=True,
        priority=5
    ).order_by('-published_at').first()

    # Destaques secundários (prioridade 3-4)
    featured_secondary = Article.objects.filter(
        is_published=True,
        is_featured=True,
        priority__in=[3, 4]
    ).order_by('-published_at')[:3]

    # Últimas notícias
    latest_news = Article.objects.filter(
        is_published=True,
        content_type='news'
    ).order_by('-published_at')[:6]

    # Entrevistas recentes
    interviews = Article.objects.filter(
        is_published=True,
        content_type='interview'
    ).order_by('-published_at')[:3]

    # Próximos eventos
    events = Article.objects.filter(
        is_published=True,
        content_type='event',
        event_date__isnull=False
    ).order_by('event_date')[:4]

    # Guias e artigos
    guides = Article.objects.filter(
        is_published=True,
        content_type__in=['guide', 'article']
    ).order_by('-published_at')[:4]

    # Dica da semana
    tip_of_week = Article.objects.filter(
        is_published=True,
        content_type='tip'
    ).order_by('-published_at').first()

    # Quizzes ativos
    quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')[:3]

    # Categorias ativas
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')

    context = {
        'breaking_news': breaking_news,
        'featured_main': featured_main,
        'featured_secondary': featured_secondary,
        'latest_news': latest_news,
        'interviews': interviews,
        'events': events,
        'guides': guides,
        'tip_of_week': tip_of_week,
        'quizzes': quizzes,
        'categories': categories,
    }

    return render(request, 'news/home.html', context)


def article_detail(request, slug):
    """Página de detalhes do artigo"""
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # Incrementar visualizações
    article.increment_views()

    # Artigos relacionados (mesma categoria ou tags)
    related_articles = Article.objects.filter(
        Q(category=article.category) | Q(tags__in=article.tags.all()),
        is_published=True
    ).exclude(id=article.id).distinct().order_by('-published_at')[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
    }

    return render(request, 'news/article_detail.html', context)


def category_articles(request, slug):
    """Lista artigos de uma categoria"""
    category = get_object_or_404(Category, slug=slug, is_active=True)

    articles_list = Article.objects.filter(
        category=category,
        is_published=True
    ).order_by('-published_at')

    # Paginação
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'category': category,
        'articles': articles,
    }

    return render(request, 'news/category_articles.html', context)


def tag_articles(request, slug):
    """Lista artigos de uma tag"""
    tag = get_object_or_404(Tag, slug=slug)

    articles_list = Article.objects.filter(
        tags=tag,
        is_published=True
    ).order_by('-published_at')

    # Paginação
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'articles': articles,
    }

    return render(request, 'news/tag_articles.html', context)


def content_type_articles(request, content_type):
    """Lista artigos por tipo de conteúdo"""

    # Validar content_type
    valid_types = dict(Article.CONTENT_TYPE_CHOICES)
    if content_type not in valid_types:
        return redirect('news:home')

    articles_list = Article.objects.filter(
        content_type=content_type,
        is_published=True
    ).order_by('-published_at')

    # Paginação
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'content_type': content_type,
        'content_type_display': valid_types[content_type],
        'articles': articles,
    }

    return render(request, 'news/content_type_articles.html', context)


def search_articles(request):
    """Busca de artigos"""
    query = request.GET.get('q', '')

    if query:
        articles_list = Article.objects.filter(
            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query),
            is_published=True
        ).order_by('-published_at')
    else:
        articles_list = Article.objects.none()

    # Paginação
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    context = {
        'query': query,
        'articles': articles,
    }

    return render(request, 'news/search.html', context)


@login_required(login_url='account_login')
def quiz_detail(request, slug):
    """Página do quiz - requer login"""
    quiz = get_object_or_404(Quiz, slug=slug, is_active=True)
    questions = quiz.questions.prefetch_related('options').all()

    context = {
        'quiz': quiz,
        'questions': questions,
    }

    return render(request, 'news/quiz_detail.html', context)


@login_required(login_url='account_login')
@require_POST
def submit_quiz(request, slug):
    """Processa resposta do quiz e concede pontos de gamificação"""
    quiz = get_object_or_404(Quiz, slug=slug, is_active=True)

    # Coletar respostas do POST
    user_answers = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            option_id = int(value)
            user_answers[question_id] = option_id

    # Calcular pontuação
    questions = quiz.questions.all()
    total_questions = questions.count()
    correct_answers = 0
    results = []

    for question in questions:
        user_option_id = user_answers.get(question.id)
        if user_option_id:
            correct_option = question.options.filter(is_correct=True).first()
            user_option = question.options.filter(id=user_option_id).first()

            is_correct = user_option and user_option.is_correct
            if is_correct:
                correct_answers += 1

            results.append({
                'question': question.question_text,
                'user_answer': user_option.option_text if user_option else 'Não respondida',
                'correct_answer': correct_option.option_text if correct_option else 'N/A',
                'is_correct': is_correct,
                'explanation': question.explanation
            })

    # Incrementar contador
    quiz.times_completed += 1
    quiz.save(update_fields=['times_completed'])

    score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0

    # ===== INTEGRAÇÃO COM GAMIFICAÇÃO =====
    # Calcular XP baseado no desempenho
    xp_earned = 0
    leveled_up = False
    old_level = 0
    new_level = 0

    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        old_level = profile.level

        # Sistema de pontos baseado no desempenho:
        # 100% = 50 XP
        # 90-99% = 40 XP
        # 80-89% = 30 XP
        # 70-79% = 20 XP
        # 60-69% = 10 XP
        # < 60% = 5 XP (participação)

        if score_percentage >= 100:
            xp_earned = 50
        elif score_percentage >= 90:
            xp_earned = 40
        elif score_percentage >= 80:
            xp_earned = 30
        elif score_percentage >= 70:
            xp_earned = 20
        elif score_percentage >= 60:
            xp_earned = 10
        else:
            xp_earned = 5  # XP de participação

        # Adicionar XP ao perfil
        new_level, leveled_up = profile.add_xp(xp_earned)

        # Registrar tentativa no histórico
        QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=correct_answers,
            total_questions=total_questions,
            score_percentage=score_percentage,
            xp_earned=xp_earned,
            leveled_up=leveled_up,
            level_before=old_level,
            level_after=new_level
        )

        # Mensagem de sucesso
        if leveled_up:
            messages.success(
                request,
                f'🎉 Parabéns! Você ganhou {xp_earned} XP e subiu para o nível {new_level}!'
            )
        else:
            messages.success(
                request,
                f'✅ Quiz concluído! Você ganhou {xp_earned} XP.'
            )

    context = {
        'quiz': quiz,
        'results': results,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'score_percentage': score_percentage,
        'xp_earned': xp_earned,
        'leveled_up': leveled_up,
        'old_level': old_level,
        'new_level': new_level,
    }

    return render(request, 'news/quiz_results.html', context)


@require_POST
def subscribe_newsletter(request):
    """Inscrição na newsletter"""
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()

    if not email:
        messages.error(request, 'Por favor, informe seu e-mail.')
        return redirect(request.META.get('HTTP_REFERER', 'news:home'))

    newsletter, created = Newsletter.objects.get_or_create(
        email=email,
        defaults={'name': name, 'is_active': True}
    )

    if created:
        messages.success(request, 'Inscrição realizada com sucesso! Você receberá nossas novidades.')
    else:
        if not newsletter.is_active:
            newsletter.is_active = True
            newsletter.unsubscribed_at = None
            newsletter.save()
            messages.success(request, 'Sua inscrição foi reativada!')
        else:
            messages.info(request, 'Este e-mail já está inscrito em nossa newsletter.')

    return redirect(request.META.get('HTTP_REFERER', 'news:home'))

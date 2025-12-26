"""
Views para Dashboard de Relatórios Modular.
Área administrativa com gráficos, exportação CSV e Markdown.
"""

import csv
from io import StringIO
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone

from core.models import Book, Author, Category, Video, Event, Section

# Importar modelos opcionais
try:
    from finance.models import Subscription, Campaign, CampaignGrant
except ImportError:
    Subscription = None
    Campaign = None
    CampaignGrant = None

try:
    from new_authors.models import EmergingAuthor, AuthorBook, Chapter
except ImportError:
    EmergingAuthor = None
    AuthorBook = None
    Chapter = None


# ============================================
# FUNÇÕES AUXILIARES DE COLETA DE DADOS
# ============================================

def get_books_module_data():
    """Coleta dados do módulo de livros."""
    total_books = Book.objects.count()
    books_with_cover = Book.objects.filter(cover_image__isnull=False).exclude(cover_image='').count()
    books_from_google = Book.objects.exclude(Q(google_books_id='') | Q(google_books_id__isnull=True)).count()
    
    # Livros por categoria
    books_by_category = Category.objects.annotate(
        book_count=Count('books')
    ).filter(book_count__gt=0).order_by('-book_count')[:10]
    
    # Top 10 autores por quantidade de livros
    top_authors = Author.objects.annotate(
        book_count=Count('books')
    ).filter(book_count__gt=0).order_by('-book_count')[:10]
    
    # Estatísticas gerais
    avg_rating = Book.objects.aggregate(avg=Avg('average_rating'))['avg'] or 0
    
    return {
        'total_books': total_books,
        'books_with_cover': books_with_cover,
        'books_without_cover': total_books - books_with_cover,
        'books_from_google': books_from_google,
        'cover_percentage': round((books_with_cover / total_books * 100), 1) if total_books > 0 else 0,
        'avg_rating': round(avg_rating, 1),
        'books_by_category': list(books_by_category.values('name', 'book_count')),
        'top_authors': list(top_authors.values('name', 'book_count')),
        'chart_labels': [c['name'] for c in books_by_category.values('name')],
        'chart_values': [c['book_count'] for c in books_by_category.values('book_count')],
    }


def get_authors_module_data():
    """Coleta dados do módulo de autores."""
    total_authors = Author.objects.count()
    
    # Autores por quantidade de livros
    authors_by_books = Author.objects.annotate(
        book_count=Count('books')
    ).order_by('-book_count')[:10]
    
    # Autores sem livros
    authors_without_books = Author.objects.annotate(
        book_count=Count('books')
    ).filter(book_count=0).count()
    
    return {
        'total_authors': total_authors,
        'authors_with_books': total_authors - authors_without_books,
        'authors_without_books': authors_without_books,
        'authors_by_books': list(authors_by_books.values('name', 'book_count')),
        'chart_labels': [a['name'] for a in authors_by_books.values('name')],
        'chart_values': [a['book_count'] for a in authors_by_books.values('book_count')],
    }


def get_videos_module_data():
    """Coleta dados do módulo de vídeos."""
    total_videos = Video.objects.count()
    
    # Estatísticas básicas
    active_videos = Video.objects.filter(active=True).count() if hasattr(Video, 'active') else total_videos
    
    return {
        'total_videos': total_videos,
        'active_videos': active_videos,
        'inactive_videos': total_videos - active_videos,
    }


def get_finance_module_data():
    """Coleta dados do módulo financeiro (se disponível)."""
    if not Subscription:
        return None
    
    now = timezone.now()
    
    # Assinaturas
    total_subscriptions = Subscription.objects.count()
    active_subscriptions = Subscription.objects.filter(
        status='ativa',
        expiration_date__gte=now
    ).count()
    
    # Receita total
    total_revenue = Subscription.objects.filter(status='ativa').aggregate(
        total=Sum('price')
    )['total'] or 0
    
    # Assinaturas por mês (últimos 6 meses)
    subscriptions_by_month = []
    for i in range(6):
        month_start = now - timedelta(days=30 * (5 - i))
        month_end = now - timedelta(days=30 * (4 - i)) if i < 5 else now
        count = Subscription.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        subscriptions_by_month.append({
            'month': month_start.strftime('%b/%y'),
            'count': count
        })
    
    # Campanhas
    if Campaign:
        total_campaigns = Campaign.objects.count()
        active_campaigns = Campaign.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).count()
    else:
        total_campaigns = 0
        active_campaigns = 0
    
    return {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'total_revenue': float(total_revenue),
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'subscriptions_by_month': subscriptions_by_month,
        'chart_labels': [s['month'] for s in subscriptions_by_month],
        'chart_values': [s['count'] for s in subscriptions_by_month],
    }


def get_events_module_data():
    """Coleta dados do módulo de eventos."""
    now = timezone.now()
    
    total_events = Event.objects.count()
    upcoming = Event.objects.filter(start_date__gt=now, active=True).count()
    happening = Event.objects.filter(start_date__lte=now, end_date__gte=now, active=True).count()
    finished = Event.objects.filter(end_date__lt=now).count()
    
    return {
        'total_events': total_events,
        'upcoming': upcoming,
        'happening': happening,
        'finished': finished,
        'chart_labels': ['Próximos', 'Acontecendo', 'Finalizados'],
        'chart_values': [upcoming, happening, finished],
    }


# ============================================
# VIEWS PRINCIPAIS
# ============================================

@staff_member_required
def reports_dashboard(request):
    """Dashboard principal de relatórios."""
    
    context = {
        'title': '',  # Removido para não mostrar texto extra
        'books_data': get_books_module_data(),
        'authors_data': get_authors_module_data(),
        'videos_data': get_videos_module_data(),
        'events_data': get_events_module_data(),
        'finance_data': get_finance_module_data(),
        'generated_at': timezone.now(),
    }
    
    return render(request, 'admin/reports_dashboard.html', context)


# ============================================
# EXPORTAÇÃO CSV
# ============================================

@staff_member_required
def export_books_csv(request):
    """Exporta lista de livros em CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="livros_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')  # BOM para Excel
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Título', 'Autor', 'Categoria', 'ISBN', 'Ano', 'Avaliação Média', 'Tem Capa'])
    
    books = Book.objects.select_related('author', 'category').all()
    for book in books:
        writer.writerow([
            book.id,
            book.title,
            book.author.name if book.author else '',
            book.category.name if book.category else '',
            getattr(book, 'isbn', ''),
            getattr(book, 'publication_year', ''),
            book.average_rating or '',
            'Sim' if book.cover_image else 'Não'
        ])
    
    return response


@staff_member_required
def export_authors_csv(request):
    """Exporta lista de autores em CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="autores_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Nome', 'Quantidade de Livros', 'Biografia'])
    
    authors = Author.objects.annotate(book_count=Count('books')).all()
    for author in authors:
        writer.writerow([
            author.id,
            author.name,
            author.book_count,
            getattr(author, 'bio', '')[:200] if hasattr(author, 'bio') else ''
        ])
    
    return response


@staff_member_required
def export_videos_csv(request):
    """Exporta lista de vídeos em CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="videos_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Título', 'URL', 'Ativo'])
    
    videos = Video.objects.all()
    for video in videos:
        writer.writerow([
            video.id,
            video.title,
            getattr(video, 'url', getattr(video, 'youtube_url', '')),
            'Sim' if getattr(video, 'active', True) else 'Não'
        ])
    
    return response


# ============================================
# EXPORTAÇÃO MARKDOWN
# ============================================

@staff_member_required
def export_books_markdown(request):
    """Exporta relatório de livros em Markdown."""
    data = get_books_module_data()
    now = datetime.now()
    
    md_content = f"""# Relatório de Livros - CGBookStore

**Gerado em:** {now.strftime('%d/%m/%Y às %H:%M')}

---

## Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| Total de Livros | {data['total_books']} |
| Livros com Capa | {data['books_with_cover']} ({data['cover_percentage']}%) |
| Livros sem Capa | {data['books_without_cover']} |
| Livros do Google Books | {data['books_from_google']} |
| Avaliação Média | {data['avg_rating']} ⭐ |

---

## Livros por Categoria

| Categoria | Quantidade |
|-----------|------------|
"""
    
    for cat in data['books_by_category']:
        md_content += f"| {cat['name']} | {cat['book_count']} |\n"
    
    md_content += """
---

## Top 10 Autores (por quantidade de livros)

| Autor | Livros |
|-------|--------|
"""
    
    for author in data['top_authors']:
        md_content += f"| {author['name']} | {author['book_count']} |\n"
    
    md_content += """
---

## Lista Completa de Livros

| Título | Autor | Categoria | Avaliação |
|--------|-------|-----------|-----------|
"""
    
    books = Book.objects.select_related('author', 'category').all()[:100]  # Limitar a 100
    for book in books:
        author_name = book.author.name if book.author else '-'
        category_name = book.category.name if book.category else '-'
        rating = f"{book.average_rating} ⭐" if book.average_rating else '-'
        md_content += f"| {book.title} | {author_name} | {category_name} | {rating} |\n"
    
    if Book.objects.count() > 100:
        md_content += f"\n*... e mais {Book.objects.count() - 100} livros não listados.*\n"
    
    response = HttpResponse(md_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio_livros_{now.strftime("%Y%m%d_%H%M")}.md"'
    return response


@staff_member_required
def export_authors_markdown(request):
    """Exporta relatório de autores em Markdown."""
    data = get_authors_module_data()
    now = datetime.now()
    
    md_content = f"""# Relatório de Autores - CGBookStore

**Gerado em:** {now.strftime('%d/%m/%Y às %H:%M')}

---

## Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| Total de Autores | {data['total_authors']} |
| Autores com Livros | {data['authors_with_books']} |
| Autores sem Livros | {data['authors_without_books']} |

---

## Top 10 Autores por Quantidade de Livros

| Posição | Autor | Livros |
|---------|-------|--------|
"""
    
    for i, author in enumerate(data['authors_by_books'], 1):
        md_content += f"| {i}º | {author['name']} | {author['book_count']} |\n"
    
    md_content += """
---

## Lista Completa de Autores

| Nome | Quantidade de Livros |
|------|---------------------|
"""
    
    authors = Author.objects.annotate(book_count=Count('books')).order_by('name')
    for author in authors:
        md_content += f"| {author.name} | {author.book_count} |\n"
    
    response = HttpResponse(md_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio_autores_{now.strftime("%Y%m%d_%H%M")}.md"'
    return response


@staff_member_required
def export_videos_markdown(request):
    """Exporta relatório de vídeos em Markdown."""
    data = get_videos_module_data()
    now = datetime.now()
    
    md_content = f"""# Relatório de Vídeos - CGBookStore

**Gerado em:** {now.strftime('%d/%m/%Y às %H:%M')}

---

## Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| Total de Vídeos | {data['total_videos']} |
| Vídeos Ativos | {data['active_videos']} |
| Vídeos Inativos | {data['inactive_videos']} |

---

## Lista de Vídeos

| Título | Status |
|--------|--------|
"""
    
    videos = Video.objects.all()
    for video in videos:
        status = '✅ Ativo' if getattr(video, 'active', True) else '❌ Inativo'
        md_content += f"| {video.title} | {status} |\n"
    
    response = HttpResponse(md_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio_videos_{now.strftime("%Y%m%d_%H%M")}.md"'
    return response


@staff_member_required
def export_finance_markdown(request):
    """Exporta relatório financeiro em Markdown."""
    data = get_finance_module_data()
    now = datetime.now()
    
    if not data:
        md_content = """# Relatório Financeiro - CGBookStore

**Módulo financeiro não disponível.**
"""
    else:
        md_content = f"""# Relatório Financeiro - CGBookStore

**Gerado em:** {now.strftime('%d/%m/%Y às %H:%M')}

---

## Estatísticas de Assinaturas

| Métrica | Valor |
|---------|-------|
| Total de Assinaturas | {data['total_subscriptions']} |
| Assinaturas Ativas | {data['active_subscriptions']} |
| Receita Total | R$ {data['total_revenue']:.2f} |

---

## Campanhas

| Métrica | Valor |
|---------|-------|
| Total de Campanhas | {data['total_campaigns']} |
| Campanhas Ativas | {data['active_campaigns']} |

---

## Assinaturas por Mês (últimos 6 meses)

| Mês | Quantidade |
|-----|------------|
"""
        for sub in data['subscriptions_by_month']:
            md_content += f"| {sub['month']} | {sub['count']} |\n"
    
    response = HttpResponse(md_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{now.strftime("%Y%m%d_%H%M")}.md"'
    return response

"""
Views adicionais para exportação de anotações.
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone

from .models import EBook, Bookmark, Highlight, ReadingNote


@login_required
def export_annotations_txt(request, book_id):
    """Exporta anotações de um livro em formato TXT."""
    ebook = get_object_or_404(EBook, id=book_id)
    
    bookmarks = Bookmark.objects.filter(user=request.user, ebook=ebook)
    highlights = Highlight.objects.filter(user=request.user, ebook=ebook)
    notes = ReadingNote.objects.filter(user=request.user, ebook=ebook)
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"ANOTAÇÕES - {ebook.title}")
    lines.append(f"Autor: {ebook.author}")
    lines.append(f"Exportado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    
    # Marcadores
    if bookmarks:
        lines.append("-" * 40)
        lines.append("📑 MARCADORES")
        lines.append("-" * 40)
        for bm in bookmarks:
            lines.append(f"• {bm.title or bm.chapter_title or 'Sem título'}")
            lines.append(f"  Criado em: {bm.created_at.strftime('%d/%m/%Y')}")
            lines.append("")
    
    # Destaques
    if highlights:
        lines.append("-" * 40)
        lines.append("✨ DESTAQUES")
        lines.append("-" * 40)
        for hl in highlights:
            lines.append(f"[{hl.get_color_display()}]")
            lines.append(f'"{hl.text}"')
            if hl.chapter_title:
                lines.append(f"  Capítulo: {hl.chapter_title}")
            lines.append("")
    
    # Notas
    if notes:
        lines.append("-" * 40)
        lines.append("📝 NOTAS")
        lines.append("-" * 40)
        for note in notes:
            lines.append(f"• {note.note_text}")
            if note.chapter_title:
                lines.append(f"  Capítulo: {note.chapter_title}")
            lines.append(f"  Criado em: {note.created_at.strftime('%d/%m/%Y')}")
            lines.append("")
    
    if not bookmarks and not highlights and not notes:
        lines.append("Nenhuma anotação encontrada para este livro.")
    
    lines.append("=" * 60)
    lines.append("Exportado via RetroReader - CGBookStore")
    lines.append("=" * 60)
    
    content = "\n".join(lines)
    
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    filename = f"anotacoes_{ebook.title[:30].replace(' ', '_')}.txt"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def export_annotations_html(request, book_id):
    """Exporta anotações de um livro em formato HTML (para impressão/PDF)."""
    ebook = get_object_or_404(EBook, id=book_id)
    
    bookmarks = Bookmark.objects.filter(user=request.user, ebook=ebook)
    highlights = Highlight.objects.filter(user=request.user, ebook=ebook)
    notes = ReadingNote.objects.filter(user=request.user, ebook=ebook)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Anotações - {ebook.title}</title>
        <style>
            body {{
                font-family: Georgia, serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #faf8f5;
                color: #333;
            }}
            h1 {{
                color: #8b4513;
                border-bottom: 2px solid #d4a574;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #5c3d2e;
                margin-top: 30px;
            }}
            .meta {{
                color: #666;
                font-style: italic;
                margin-bottom: 30px;
            }}
            .bookmark, .highlight, .note {{
                background: #fff;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #d4a574;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .highlight {{
                border-left-color: #f0c040;
            }}
            .highlight.green {{
                border-left-color: #4caf50;
            }}
            .highlight.blue {{
                border-left-color: #2196f3;
            }}
            .highlight.pink {{
                border-left-color: #e91e63;
            }}
            .highlight.orange {{
                border-left-color: #ff9800;
            }}
            .note {{
                border-left-color: #9c27b0;
            }}
            .chapter {{
                font-size: 0.85em;
                color: #888;
            }}
            .date {{
                font-size: 0.8em;
                color: #aaa;
            }}
            blockquote {{
                font-style: italic;
                margin: 0;
                padding: 0;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                color: #888;
                font-size: 0.9em;
            }}
            @media print {{
                body {{ background: white; }}
                .bookmark, .highlight, .note {{ box-shadow: none; border: 1px solid #ddd; }}
            }}
        </style>
    </head>
    <body>
        <h1>📚 {ebook.title}</h1>
        <p class="meta">
            <strong>Autor:</strong> {ebook.author}<br>
            <strong>Exportado em:</strong> {timezone.now().strftime('%d/%m/%Y às %H:%M')}
        </p>
    """
    
    if bookmarks:
        html_content += "<h2>📑 Marcadores</h2>"
        for bm in bookmarks:
            html_content += f"""
            <div class="bookmark">
                <strong>{bm.title or bm.chapter_title or 'Marcador'}</strong>
                <span class="date">({bm.created_at.strftime('%d/%m/%Y')})</span>
            </div>
            """
    
    if highlights:
        html_content += "<h2>✨ Destaques</h2>"
        for hl in highlights:
            html_content += f"""
            <div class="highlight {hl.color}">
                <blockquote>"{hl.text}"</blockquote>
                {"<p class='chapter'>Capítulo: " + hl.chapter_title + "</p>" if hl.chapter_title else ""}
            </div>
            """
    
    if notes:
        html_content += "<h2>📝 Notas</h2>"
        for note in notes:
            html_content += f"""
            <div class="note">
                <p>{note.note_text}</p>
                {"<p class='chapter'>Capítulo: " + note.chapter_title + "</p>" if note.chapter_title else ""}
                <span class="date">{note.created_at.strftime('%d/%m/%Y')}</span>
            </div>
            """
    
    if not bookmarks and not highlights and not notes:
        html_content += "<p>Nenhuma anotação encontrada para este livro.</p>"
    
    html_content += """
        <div class="footer">
            <p>📺 Exportado via <strong>RetroReader</strong> - CGBookStore</p>
        </div>
    </body>
    </html>
    """
    
    response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
    filename = f"anotacoes_{ebook.title[:30].replace(' ', '_')}.html"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def export_all_annotations(request):
    """Exporta todas as anotações do usuário em formato TXT."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('ebook')
    highlights = Highlight.objects.filter(user=request.user).select_related('ebook')
    notes = ReadingNote.objects.filter(user=request.user).select_related('ebook')
    
    lines = []
    lines.append("=" * 60)
    lines.append("TODAS AS MINHAS ANOTAÇÕES - RetroReader")
    lines.append(f"Usuário: {request.user.username}")
    lines.append(f"Exportado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    
    # Agrupar por livro
    books_data = {}
    
    for bm in bookmarks:
        book_key = bm.ebook.title
        if book_key not in books_data:
            books_data[book_key] = {'bookmarks': [], 'highlights': [], 'notes': [], 'author': bm.ebook.author}
        books_data[book_key]['bookmarks'].append(bm)
    
    for hl in highlights:
        book_key = hl.ebook.title
        if book_key not in books_data:
            books_data[book_key] = {'bookmarks': [], 'highlights': [], 'notes': [], 'author': hl.ebook.author}
        books_data[book_key]['highlights'].append(hl)
    
    for note in notes:
        book_key = note.ebook.title
        if book_key not in books_data:
            books_data[book_key] = {'bookmarks': [], 'highlights': [], 'notes': [], 'author': note.ebook.author}
        books_data[book_key]['notes'].append(note)
    
    for title, data in books_data.items():
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"📖 {title}")
        lines.append(f"   Autor: {data['author']}")
        lines.append("=" * 60)
        
        if data['bookmarks']:
            lines.append("")
            lines.append("📑 Marcadores:")
            for bm in data['bookmarks']:
                lines.append(f"  • {bm.title or bm.chapter_title or 'Sem título'}")
        
        if data['highlights']:
            lines.append("")
            lines.append("✨ Destaques:")
            for hl in data['highlights']:
                lines.append(f'  "{hl.text[:100]}{"..." if len(hl.text) > 100 else ""}"')
        
        if data['notes']:
            lines.append("")
            lines.append("📝 Notas:")
            for note in data['notes']:
                lines.append(f"  • {note.note_text[:100]}{'...' if len(note.note_text) > 100 else ''}")
    
    if not books_data:
        lines.append("Você ainda não tem anotações.")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("Exportado via RetroReader - CGBookStore")
    lines.append("=" * 60)
    
    content = "\n".join(lines)
    
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="minhas_anotacoes_retroreader.txt"'
    
    return response

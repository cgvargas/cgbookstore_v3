from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    EBook, UserLibrary, UserBookProgress, 
    Bookmark, Highlight, ReadingNote, ReaderSettings
)
from .services.gutenberg import GutenbergService
from .services.openlibrary import OpenLibraryService


class BookListAPI(APIView):
    """Lista de e-books disponíveis."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        queryset = EBook.objects.filter(is_active=True)
        
        # Filtros
        source = request.query_params.get('source')
        language = request.query_params.get('language')
        search = request.query_params.get('q')
        
        if source:
            queryset = queryset.filter(source=source)
        if language:
            queryset = queryset.filter(language=language)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        
        # Limitar resultados
        limit = int(request.query_params.get('limit', 50))
        queryset = queryset[:limit]
        
        books = []
        for book in queryset:
            books.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'cover_image': book.cover_image,
                'language': book.language,
                'source': book.source,
            })
        
        return Response({'books': books})


class BookDetailAPI(APIView):
    """Detalhes de um e-book."""
    permission_classes = [AllowAny]
    
    def get(self, request, book_id):
        book = get_object_or_404(EBook, id=book_id, is_active=True)
        
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'cover_image': book.cover_image,
            'language': book.language,
            'source': book.source,
            'publisher': book.publisher,
            'publish_year': book.publish_year,
            'subjects': book.subjects,
            'epub_url': book.get_epub_url(),
        }
        
        return Response(data)


class BookContentAPI(APIView):
    """Retorna URL do conteúdo EPUB do livro."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id):
        book = get_object_or_404(EBook, id=book_id, is_active=True)
        
        epub_url = book.get_epub_url()
        if not epub_url:
            return Response(
                {'error': 'EPUB não disponível para este livro'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({'epub_url': epub_url})


class ProgressAPI(APIView):
    """Obtém progresso de leitura."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id):
        progress = UserBookProgress.objects.filter(
            user=request.user,
            ebook_id=book_id
        ).first()
        
        if not progress:
            return Response({
                'current_cfi': '',
                'percentage': 0,
                'current_chapter': 0,
            })
        
        return Response({
            'current_cfi': progress.current_cfi,
            'percentage': float(progress.percentage),
            'current_chapter': progress.current_chapter,
            'is_finished': progress.is_finished,
            'total_reading_time': progress.total_reading_time,
        })


class SaveProgressAPI(APIView):
    """Salva progresso de leitura."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, book_id):
        book = get_object_or_404(EBook, id=book_id)
        
        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            ebook=book
        )
        
        # Atualizar campos
        if 'current_cfi' in request.data:
            progress.current_cfi = request.data['current_cfi']
        if 'percentage' in request.data:
            progress.percentage = request.data['percentage']
        if 'current_chapter' in request.data:
            progress.current_chapter = request.data['current_chapter']
        if 'session_duration' in request.data:
            progress.last_session_duration = request.data['session_duration']
            progress.total_reading_time += request.data['session_duration']
        
        # Verificar se terminou
        if progress.percentage >= 100 and not progress.is_finished:
            progress.mark_as_finished()
        else:
            progress.save()
        
        return Response({'success': True})


class BookmarkListAPI(APIView):
    """Lista todos os marcadores do usuário."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('ebook')
        
        data = []
        for bm in bookmarks:
            data.append({
                'id': bm.id,
                'book_id': bm.ebook_id,
                'book_title': bm.ebook.title,
                'cfi': bm.cfi,
                'title': bm.title,
                'chapter_title': bm.chapter_title,
                'created_at': bm.created_at.isoformat(),
            })
        
        return Response({'bookmarks': data})


class BookBookmarksAPI(APIView):
    """Lista marcadores de um livro específico."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id):
        bookmarks = Bookmark.objects.filter(
            user=request.user,
            ebook_id=book_id
        ).order_by('created_at')
        
        data = []
        for bm in bookmarks:
            data.append({
                'id': bm.id,
                'cfi': bm.cfi,
                'title': bm.title,
                'chapter_title': bm.chapter_title,
                'created_at': bm.created_at.isoformat(),
            })
        
        return Response({'bookmarks': data})


class CreateBookmarkAPI(APIView):
    """Cria um novo marcador."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        book = get_object_or_404(EBook, id=request.data.get('book_id'))
        
        bookmark = Bookmark.objects.create(
            user=request.user,
            ebook=book,
            cfi=request.data.get('cfi', ''),
            title=request.data.get('title', ''),
            chapter_title=request.data.get('chapter_title', ''),
        )
        
        return Response({
            'id': bookmark.id,
            'success': True,
        }, status=status.HTTP_201_CREATED)


class DeleteBookmarkAPI(APIView):
    """Remove um marcador."""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        Bookmark.objects.filter(id=pk, user=request.user).delete()
        return Response({'success': True})


class HighlightListAPI(APIView):
    """Lista todos os destaques do usuário."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        highlights = Highlight.objects.filter(user=request.user).select_related('ebook')
        
        data = []
        for hl in highlights:
            data.append({
                'id': hl.id,
                'book_id': hl.ebook_id,
                'book_title': hl.ebook.title,
                'cfi_range': hl.cfi_range,
                'text': hl.text,
                'color': hl.color,
                'chapter_title': hl.chapter_title,
                'created_at': hl.created_at.isoformat(),
            })
        
        return Response({'highlights': data})


class BookHighlightsAPI(APIView):
    """Lista destaques de um livro específico."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id):
        highlights = Highlight.objects.filter(
            user=request.user,
            ebook_id=book_id
        ).order_by('created_at')
        
        data = []
        for hl in highlights:
            data.append({
                'id': hl.id,
                'cfi_range': hl.cfi_range,
                'text': hl.text,
                'color': hl.color,
                'chapter_title': hl.chapter_title,
                'created_at': hl.created_at.isoformat(),
            })
        
        return Response({'highlights': data})


class CreateHighlightAPI(APIView):
    """Cria um novo destaque."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        book = get_object_or_404(EBook, id=request.data.get('book_id'))
        
        highlight = Highlight.objects.create(
            user=request.user,
            ebook=book,
            cfi_range=request.data.get('cfi_range', ''),
            text=request.data.get('text', ''),
            color=request.data.get('color', 'yellow'),
            chapter_title=request.data.get('chapter_title', ''),
        )
        
        return Response({
            'id': highlight.id,
            'success': True,
        }, status=status.HTTP_201_CREATED)


class DeleteHighlightAPI(APIView):
    """Remove um destaque."""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        Highlight.objects.filter(id=pk, user=request.user).delete()
        return Response({'success': True})


class NoteListAPI(APIView):
    """Lista todas as notas do usuário."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notes = ReadingNote.objects.filter(user=request.user).select_related('ebook')
        
        data = []
        for n in notes:
            data.append({
                'id': n.id,
                'book_id': n.ebook_id,
                'book_title': n.ebook.title,
                'cfi': n.cfi,
                'note_text': n.note_text,
                'chapter_title': n.chapter_title,
                'created_at': n.created_at.isoformat(),
            })
        
        return Response({'notes': data})


class BookNotesAPI(APIView):
    """Lista notas de um livro específico."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id):
        notes = ReadingNote.objects.filter(
            user=request.user,
            ebook_id=book_id
        ).order_by('created_at')
        
        data = []
        for n in notes:
            data.append({
                'id': n.id,
                'cfi': n.cfi,
                'note_text': n.note_text,
                'chapter_title': n.chapter_title,
                'created_at': n.created_at.isoformat(),
            })
        
        return Response({'notes': data})


class CreateNoteAPI(APIView):
    """Cria uma nova nota."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        book = get_object_or_404(EBook, id=request.data.get('book_id'))
        
        note = ReadingNote.objects.create(
            user=request.user,
            ebook=book,
            cfi=request.data.get('cfi', ''),
            note_text=request.data.get('note_text', ''),
            chapter_title=request.data.get('chapter_title', ''),
        )
        
        return Response({
            'id': note.id,
            'success': True,
        }, status=status.HTTP_201_CREATED)


class UpdateNoteAPI(APIView):
    """Atualiza uma nota existente."""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        note = get_object_or_404(ReadingNote, id=pk, user=request.user)
        
        if 'note_text' in request.data:
            note.note_text = request.data['note_text']
            note.save()
        
        return Response({'success': True})


class DeleteNoteAPI(APIView):
    """Remove uma nota."""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        ReadingNote.objects.filter(id=pk, user=request.user).delete()
        return Response({'success': True})


class ReaderSettingsAPI(APIView):
    """Obtém e atualiza configurações do leitor."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        settings, _ = ReaderSettings.objects.get_or_create(user=request.user)
        
        return Response({
            'theme': settings.theme,
            'font_family': settings.font_family,
            'font_size': settings.font_size,
            'line_height': float(settings.line_height),
            'scanlines_enabled': settings.scanlines_enabled,
            'crt_curvature': settings.crt_curvature,
            'screen_glow': settings.screen_glow,
            'sound_effects': settings.sound_effects,
            'auto_save_progress': settings.auto_save_progress,
        })
    
    def put(self, request):
        settings, _ = ReaderSettings.objects.get_or_create(user=request.user)
        
        # Atualizar campos
        fields = ['theme', 'font_family', 'font_size', 'line_height',
                  'scanlines_enabled', 'crt_curvature', 'screen_glow',
                  'sound_effects', 'auto_save_progress']
        
        for field in fields:
            if field in request.data:
                setattr(settings, field, request.data[field])
        
        settings.save()
        return Response({'success': True})


class SearchGutenbergAPI(APIView):
    """Busca livros no Project Gutenberg."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'books': []})
        
        service = GutenbergService()
        books = service.search(query)
        
        return Response({'books': books})


class SearchOpenLibraryAPI(APIView):
    """Busca livros na Open Library."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'books': []})
        
        service = OpenLibraryService()
        books = service.search(query)
        
        return Response({'books': books})


class ImportBookAPI(APIView):
    """Importa um livro de fonte externa."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, source, external_id):
        # Verificar se já existe
        existing = EBook.objects.filter(source=source, external_id=external_id).first()
        if existing:
            return Response({
                'id': existing.id,
                'message': 'Livro já existe na biblioteca',
                'already_exists': True,
            })
        
        # Importar baseado na fonte
        if source == 'gutenberg':
            service = GutenbergService()
            book_data = service.get_book(external_id)
        elif source == 'openlibrary':
            service = OpenLibraryService()
            book_data = service.get_book(external_id)
        else:
            return Response(
                {'error': 'Fonte não suportada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not book_data:
            return Response(
                {'error': 'Livro não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Criar EBook
        ebook = EBook.objects.create(
            title=book_data.get('title', 'Sem título'),
            author=book_data.get('author', 'Autor desconhecido'),
            description=book_data.get('description', ''),
            cover_image=book_data.get('cover_image', ''),
            epub_url=book_data.get('epub_url', ''),
            source=source,
            external_id=external_id,
            language=book_data.get('language', 'en'),
            subjects=book_data.get('subjects', []),
            is_public_domain=True,
        )
        
        return Response({
            'id': ebook.id,
            'message': 'Livro importado com sucesso!',
            'already_exists': False,
        }, status=status.HTTP_201_CREATED)

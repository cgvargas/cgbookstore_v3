from django.urls import path
from . import api

app_name = 'ereader_api'

urlpatterns = [
    # Livros
    path('books/', api.BookListAPI.as_view(), name='book_list'),
    path('books/<int:book_id>/', api.BookDetailAPI.as_view(), name='book_detail'),
    path('books/<int:book_id>/content/', api.BookContentAPI.as_view(), name='book_content'),
    
    # Progresso
    path('progress/<int:book_id>/', api.ProgressAPI.as_view(), name='progress'),
    path('progress/<int:book_id>/save/', api.SaveProgressAPI.as_view(), name='save_progress'),
    
    # Marcadores
    path('bookmarks/', api.BookmarkListAPI.as_view(), name='bookmark_list'),
    path('bookmarks/<int:book_id>/', api.BookBookmarksAPI.as_view(), name='book_bookmarks'),
    path('bookmarks/create/', api.CreateBookmarkAPI.as_view(), name='create_bookmark'),
    path('bookmarks/<int:pk>/delete/', api.DeleteBookmarkAPI.as_view(), name='delete_bookmark'),
    
    # Destaques
    path('highlights/', api.HighlightListAPI.as_view(), name='highlight_list'),
    path('highlights/<int:book_id>/', api.BookHighlightsAPI.as_view(), name='book_highlights'),
    path('highlights/create/', api.CreateHighlightAPI.as_view(), name='create_highlight'),
    path('highlights/<int:pk>/delete/', api.DeleteHighlightAPI.as_view(), name='delete_highlight'),
    
    # Notas
    path('notes/', api.NoteListAPI.as_view(), name='note_list'),
    path('notes/<int:book_id>/', api.BookNotesAPI.as_view(), name='book_notes'),
    path('notes/create/', api.CreateNoteAPI.as_view(), name='create_note'),
    path('notes/<int:pk>/update/', api.UpdateNoteAPI.as_view(), name='update_note'),
    path('notes/<int:pk>/delete/', api.DeleteNoteAPI.as_view(), name='delete_note'),
    
    # Configurações
    path('settings/', api.ReaderSettingsAPI.as_view(), name='settings'),
    
    # Busca externa
    path('search/gutenberg/', api.SearchGutenbergAPI.as_view(), name='search_gutenberg'),
    path('search/openlibrary/', api.SearchOpenLibraryAPI.as_view(), name='search_openlibrary'),
    path('import/<str:source>/<str:external_id>/', api.ImportBookAPI.as_view(), name='import_book'),
]

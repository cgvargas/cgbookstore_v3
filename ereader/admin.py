from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EBook, UserLibrary, UserBookProgress, 
    Bookmark, Highlight, ReadingNote, ReaderSettings
)


@admin.register(EBook)
class EBookAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de E-Books."""
    
    list_display = ['title', 'author', 'source', 'language', 'is_public_domain', 
                    'view_count', 'read_count', 'is_active', 'created_at']
    list_filter = ['source', 'language', 'is_public_domain', 'is_active', 'created_at']
    search_fields = ['title', 'author', 'description', 'external_id']
    readonly_fields = ['view_count', 'read_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'author', 'description')
        }),
        ('Arquivos', {
            'fields': ('cover_image', 'epub_file', 'epub_url')
        }),
        ('Metadados', {
            'fields': ('source', 'external_id', 'language', 'publisher', 
                       'publish_year', 'subjects')
        }),
        ('Status', {
            'fields': ('is_public_domain', 'is_active')
        }),
        ('Estatísticas', {
            'fields': ('view_count', 'read_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.cover_image)
        return '-'
    cover_preview.short_description = 'Capa'


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    """Admin para biblioteca do usuário."""
    
    list_display = ['user', 'ebook', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'ebook__title']
    raw_id_fields = ['user', 'ebook']


@admin.register(UserBookProgress)
class UserBookProgressAdmin(admin.ModelAdmin):
    """Admin para progresso de leitura."""
    
    list_display = ['user', 'ebook', 'percentage', 'current_chapter', 
                    'is_finished', 'last_read']
    list_filter = ['is_finished', 'last_read']
    search_fields = ['user__username', 'ebook__title']
    raw_id_fields = ['user', 'ebook']
    readonly_fields = ['started_at', 'last_read', 'finished_at']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """Admin para marcadores."""
    
    list_display = ['user', 'ebook', 'title', 'chapter_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'ebook__title', 'title']
    raw_id_fields = ['user', 'ebook']


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    """Admin para destaques."""
    
    list_display = ['user', 'ebook', 'text_preview', 'color', 'created_at']
    list_filter = ['color', 'created_at']
    search_fields = ['user__username', 'ebook__title', 'text']
    raw_id_fields = ['user', 'ebook']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Texto'


@admin.register(ReadingNote)
class ReadingNoteAdmin(admin.ModelAdmin):
    """Admin para notas de leitura."""
    
    list_display = ['user', 'ebook', 'note_preview', 'chapter_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'ebook__title', 'note_text']
    raw_id_fields = ['user', 'ebook', 'highlight']
    
    def note_preview(self, obj):
        return obj.note_text[:50] + '...' if len(obj.note_text) > 50 else obj.note_text
    note_preview.short_description = 'Nota'


@admin.register(ReaderSettings)
class ReaderSettingsAdmin(admin.ModelAdmin):
    """Admin para configurações do leitor."""
    
    list_display = ['user', 'theme', 'font_family', 'font_size', 
                    'scanlines_enabled', 'sound_effects']
    list_filter = ['theme', 'font_family', 'scanlines_enabled']
    search_fields = ['user__username']
    raw_id_fields = ['user']

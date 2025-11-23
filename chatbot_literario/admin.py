"""
Administração Django para o Chatbot Literário.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ChatSession, ChatMessage, ConversationContext


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin para ChatSession."""
    list_display = ['id', 'user', 'title_short', 'messages_count', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def title_short(self, obj):
        """Exibe título curto."""
        return obj.title[:50] if obj.title else '(Sem título)'
    title_short.short_description = 'Título'

    def messages_count(self, obj):
        """Exibe número de mensagens."""
        count = obj.get_messages_count()
        return format_html('<strong>{}</strong>', count)
    messages_count.short_description = 'Mensagens'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin para ChatMessage."""
    list_display = ['id', 'session', 'role_badge', 'content_preview', 'created_at', 'tokens_used', 'response_time']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'session__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        """Exibe prévia do conteúdo."""
        preview = obj.content[:100]
        if len(obj.content) > 100:
            preview += '...'
        return preview
    content_preview.short_description = 'Conteúdo'

    def role_badge(self, obj):
        """Exibe badge colorido para o papel."""
        if obj.role == 'user':
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">👤 Usuário</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">🤖 Assistente</span>'
            )
    role_badge.short_description = 'Papel'


@admin.register(ConversationContext)
class ConversationContextAdmin(admin.ModelAdmin):
    """Admin para ConversationContext."""
    list_display = ['id', 'user', 'genres_count', 'authors_count', 'interests_count', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

    def genres_count(self, obj):
        """Número de gêneros favoritos."""
        return len(obj.favorite_genres)
    genres_count.short_description = 'Gêneros'

    def authors_count(self, obj):
        """Número de autores favoritos."""
        return len(obj.favorite_authors)
    authors_count.short_description = 'Autores'

    def interests_count(self, obj):
        """Número de interesses."""
        return len(obj.interests)
    interests_count.short_description = 'Interesses'

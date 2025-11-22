from django.contrib import admin
from .models import ChatConversation


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    """
    Administração do histórico de conversas do chatbot.
    """
    list_display = ['user', 'role', 'message_preview', 'session_id', 'created_at']
    list_filter = ['role', 'created_at', 'user']
    search_fields = ['user__username', 'message', 'session_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Informações da Mensagem', {
            'fields': ('user', 'role', 'message', 'session_id')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def message_preview(self, obj):
        """Retorna uma prévia da mensagem (primeiros 100 caracteres)."""
        if len(obj.message) > 100:
            return obj.message[:100] + '...'
        return obj.message
    message_preview.short_description = 'Prévia da Mensagem'

    def has_add_permission(self, request):
        """Desabilita adição manual via admin (mensagens vêm do chatbot)."""
        return False

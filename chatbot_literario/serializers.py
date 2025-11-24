"""
Serializers para a API REST do Chatbot Literário.
"""
from rest_framework import serializers
from .models import ChatSession, ChatMessage, ConversationContext


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer para mensagens de chat."""

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'role',
            'content',
            'created_at',
            'tokens_used',
            'response_time'
        ]
        read_only_fields = ['id', 'created_at', 'tokens_used', 'response_time']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer para sessões de chat."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    messages_count = serializers.IntegerField(source='get_messages_count', read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id',
            'title',
            'is_active',
            'created_at',
            'updated_at',
            'messages_count',
            'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages_count']


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de sessões (sem mensagens)."""
    messages_count = serializers.IntegerField(source='get_messages_count', read_only=True)
    last_message_time = serializers.DateTimeField(source='get_last_message_time', read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id',
            'title',
            'is_active',
            'created_at',
            'updated_at',
            'messages_count',
            'last_message_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages_count', 'last_message_time']


class SendMessageSerializer(serializers.Serializer):
    """Serializer para enviar uma mensagem ao chatbot."""
    message = serializers.CharField(required=True, allow_blank=False, max_length=5000)
    session_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_message(self, value):
        """Valida a mensagem do usuário."""
        if not value.strip():
            raise serializers.ValidationError("A mensagem não pode estar vazia.")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer para a resposta do chatbot."""
    session_id = serializers.IntegerField()
    user_message = ChatMessageSerializer()
    bot_message = ChatMessageSerializer()
    session_title = serializers.CharField()


class ConversationContextSerializer(serializers.ModelSerializer):
    """Serializer para contexto de conversa."""

    class Meta:
        model = ConversationContext
        fields = [
            'favorite_genres',
            'favorite_authors',
            'reading_preferences',
            'interests',
            'updated_at'
        ]
        read_only_fields = ['updated_at']

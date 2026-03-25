"""
Administração Django para o Chatbot Literário.
Inclui interface para correções e gerenciamento da Knowledge Base.
"""
import logging
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ChatSession, ChatMessage, ConversationContext, ChatbotKnowledge

logger = logging.getLogger(__name__)


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
    """Admin para ChatMessage com suporte a correções."""
    list_display = [
        'id',
        'session',
        'role_badge',
        'content_preview',
        'has_correction_badge',
        'knowledge_used_badge',
        'created_at'
    ]
    list_filter = ['role', 'has_correction', 'created_at', 'rag_intent_detected']
    search_fields = ['content', 'session__user__username', 'corrected_content']
    readonly_fields = ['created_at', 'tokens_used', 'response_time']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('session', 'role', 'content', 'created_at')
        }),
        ('Metadados RAG/Knowledge Base', {
            'fields': ('rag_intent_detected', 'rag_data_used', 'knowledge_base_used'),
            'classes': ('collapse',)
        }),
        ('Correção (se aplicável)', {
            'fields': (
                'has_correction',
                'corrected_content',
                'corrected_by',
                'corrected_at'
            ),
            'description': 'Marque "Tem Correção" e preencha "Conteúdo Corrigido". '
                           'Ao salvar, a correção será automaticamente adicionada à Knowledge Base.'
        }),
        ('Feedback e Performance', {
            'fields': ('user_feedback', 'tokens_used', 'response_time'),
            'classes': ('collapse',)
        }),
    )

    actions = ['create_knowledge_from_correction', 'mark_as_corrected']

    # Mapeamento de intent types para KNOWLEDGE_TYPES válidos do modelo
    INTENT_TO_KNOWLEDGE_TYPE = {
        'author_query': 'author_query',
        'author_search': 'author_query',
        'book_detail': 'book_info',
        'book_recommendation': 'recommendation',
        'book_reference': 'book_info',
        'series_info': 'series_info',
        'category_search': 'category_search',
        'franchise_info': 'general',
        'adaptation_info': 'general',
    }

    def save_model(self, request, obj, form, change):
        """
        Override para auto-salvar correções na Knowledge Base.
        
        Quando o admin marca has_correction=True e preenche corrected_content,
        a correção é automaticamente salva na Knowledge Base para uso futuro.
        """
        # Verificar se é uma correção nova (has_correction mudou para True)
        if obj.has_correction and obj.corrected_content and obj.role == 'assistant':
            # Preencher campos de correção automaticamente
            if not obj.corrected_by:
                obj.corrected_by = request.user
            if not obj.corrected_at:
                obj.corrected_at = timezone.now()

        super().save_model(request, obj, form, change)

        # Auto-criar entrada na Knowledge Base
        if obj.has_correction and obj.corrected_content and obj.role == 'assistant':
            self._auto_create_knowledge(request, obj)

    def _auto_create_knowledge(self, request, message):
        """Cria automaticamente entrada na Knowledge Base a partir de uma correção."""
        from .knowledge_base_service import get_knowledge_service

        try:
            kb_service = get_knowledge_service()

            # Encontrar mensagem do usuário anterior (pergunta)
            user_message = message.session.messages.filter(
                role='user',
                created_at__lt=message.created_at
            ).order_by('-created_at').first()

            if not user_message:
                return

            # Mapear intent type para knowledge_type válido
            raw_type = message.rag_intent_detected or 'general'
            knowledge_type = self.INTENT_TO_KNOWLEDGE_TYPE.get(raw_type, 'general')

            # Verificar se já existe entrada para esta pergunta
            from .models import ChatbotKnowledge
            existing = ChatbotKnowledge.objects.filter(
                original_question__iexact=user_message.content
            ).first()

            if existing:
                # Atualizar entrada existente
                existing.correct_response = message.corrected_content
                existing.incorrect_response = message.content
                existing.confidence_score = 1.0
                existing.is_active = True
                existing.save()
                logger.info(f"✅ Knowledge Base ATUALIZADO: ID={existing.id}")
            else:
                # Criar nova entrada
                kb_service.add_correction(
                    original_question=user_message.content,
                    incorrect_response=message.content,
                    correct_response=message.corrected_content,
                    knowledge_type=knowledge_type,
                    created_by=request.user,
                    confidence_score=1.0
                )
                logger.info(f"✅ Knowledge Base: Nova correção auto-salva para '{user_message.content[:50]}'")

        except Exception as e:
            logger.error(f"Erro ao auto-salvar no Knowledge Base: {e}", exc_info=True)

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

    def has_correction_badge(self, obj):
        """Badge indicando se tem correção."""
        if obj.has_correction:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">✏️ Corrigido</span>'
            )
        return format_html(
            '<span style="color: #999;">—</span>'
        )
    has_correction_badge.short_description = 'Correção'

    def knowledge_used_badge(self, obj):
        """Badge indicando se usou Knowledge Base."""
        if obj.knowledge_base_used:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 3px;">🧠 KB</span>'
            )
        return format_html(
            '<span style="color: #999;">—</span>'
        )
    knowledge_used_badge.short_description = 'KB Usado'

    def create_knowledge_from_correction(self, request, queryset):
        """Action: Cria entrada na Knowledge Base a partir de correções."""
        from .knowledge_base_service import get_knowledge_service

        kb_service = get_knowledge_service()
        count = 0

        for message in queryset.filter(has_correction=True, role='assistant'):
            # Encontrar mensagem do usuário anterior (pergunta)
            user_message = message.session.messages.filter(
                role='user',
                created_at__lt=message.created_at
            ).order_by('-created_at').first()

            if user_message:
                # Detectar tipo de conhecimento baseado no RAG intent
                knowledge_type = message.rag_intent_detected or 'general'

                # Criar entrada na Knowledge Base
                kb_service.add_correction(
                    original_question=user_message.content,
                    incorrect_response=message.content,
                    correct_response=message.corrected_content,
                    knowledge_type=knowledge_type,
                    created_by=request.user,
                    confidence_score=1.0
                )
                count += 1

        self.message_user(
            request,
            f"✅ {count} correção(ões) adicionada(s) à Knowledge Base com sucesso!"
        )

    create_knowledge_from_correction.short_description = "🧠 Criar Knowledge a partir de correções selecionadas"

    def mark_as_corrected(self, request, queryset):
        """Action: Marca mensagens como corrigidas."""
        updated = queryset.update(
            has_correction=True,
            corrected_by=request.user,
            corrected_at=timezone.now()
        )
        self.message_user(request, f"✅ {updated} mensagem(ns) marcada(s) como corrigida(s).")

    mark_as_corrected.short_description = "✏️ Marcar como corrigido"


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


# ==============================================================================
# KNOWLEDGE BASE ADMIN
# ==============================================================================


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar a Base de Conhecimento do Chatbot.

    Permite visualizar, editar e gerenciar correções aprendidas.
    """
    list_display = [
        'id',
        'knowledge_type_badge',
        'question_preview',
        'times_used_badge',
        'confidence_badge',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'knowledge_type',
        'is_active',
        'created_at',
        'confidence_score'
    ]

    search_fields = [
        'original_question',
        'correct_response',
        'keywords',
        'admin_notes'
    ]

    readonly_fields = [
        'times_used',
        'last_used_at',
        'created_at',
        'updated_at',
        'keywords'
    ]

    date_hierarchy = 'created_at'

    fieldsets = (
        ('Pergunta Original', {
            'fields': ('knowledge_type', 'original_question', 'keywords')
        }),
        ('Respostas', {
            'fields': ('incorrect_response', 'correct_response'),
            'description': 'Resposta incorreta (referência) e resposta correta'
        }),
        ('Relacionamentos', {
            'fields': ('related_book', 'related_author'),
            'classes': ('collapse',),
            'description': 'Livro ou autor relacionado a esta correção (opcional)'
        }),
        ('Controle de Qualidade', {
            'fields': ('is_active', 'confidence_score', 'admin_notes'),
            'description': 'Confiança: 0.0 (baixa) a 1.0 (alta). Maior confiança = maior prioridade'
        }),
        ('Estatísticas', {
            'fields': ('times_used', 'last_used_at', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_knowledge', 'deactivate_knowledge', 'increase_confidence', 'decrease_confidence']

    def question_preview(self, obj):
        """Prévia da pergunta."""
        return obj.original_question[:80] + ('...' if len(obj.original_question) > 80 else '')
    question_preview.short_description = 'Pergunta'

    def knowledge_type_badge(self, obj):
        """Badge colorido para tipo de conhecimento."""
        colors = {
            'author_query': '#007bff',
            'book_info': '#28a745',
            'recommendation': '#ffc107',
            'series_info': '#17a2b8',
            'category_search': '#6f42c1',
            'general': '#6c757d',
        }
        color = colors.get(obj.knowledge_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_knowledge_type_display()
        )
    knowledge_type_badge.short_description = 'Tipo'

    def times_used_badge(self, obj):
        """Badge com número de vezes usado."""
        if obj.times_used == 0:
            color = '#6c757d'
        elif obj.times_used < 5:
            color = '#28a745'
        elif obj.times_used < 20:
            color = '#ffc107'
        else:
            color = '#dc3545'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.times_used
        )
    times_used_badge.short_description = 'Usos'

    def confidence_badge(self, obj):
        """Badge de confiança."""
        if obj.confidence_score >= 0.9:
            color = '#28a745'
            label = 'Alta'
        elif obj.confidence_score >= 0.7:
            color = '#ffc107'
            label = 'Média'
        else:
            color = '#dc3545'
            label = 'Baixa'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} ({})</span>',
            color,
            label,
            f"{obj.confidence_score:.0%}"
        )
    confidence_badge.short_description = 'Confiança'

    def activate_knowledge(self, request, queryset):
        """Ativa conhecimentos selecionados."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ {updated} conhecimento(s) ativado(s).")
    activate_knowledge.short_description = "✅ Ativar conhecimentos selecionados"

    def deactivate_knowledge(self, request, queryset):
        """Desativa conhecimentos selecionados."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"⛔ {updated} conhecimento(s) desativado(s).")
    deactivate_knowledge.short_description = "⛔ Desativar conhecimentos selecionados"

    def increase_confidence(self, request, queryset):
        """Aumenta confiança em 0.1."""
        for knowledge in queryset:
            knowledge.confidence_score = min(1.0, knowledge.confidence_score + 0.1)
            knowledge.save()
        self.message_user(request, f"⬆️ Confiança aumentada para {queryset.count()} conhecimento(s).")
    increase_confidence.short_description = "⬆️ Aumentar confiança (+0.1)"

    def decrease_confidence(self, request, queryset):
        """Diminui confiança em 0.1."""
        for knowledge in queryset:
            knowledge.confidence_score = max(0.0, knowledge.confidence_score - 0.1)
            knowledge.save()
        self.message_user(request, f"⬇️ Confiança diminuída para {queryset.count()} conhecimento(s).")
    decrease_confidence.short_description = "⬇️ Diminuir confiança (-0.1)"

"""
Interface Admin para o Sistema de Monitoramento.

Fornece painéis completos para revisar atividades suspeitas e
alertas de IA, com ações em massa e envio manual de WhatsApp.
"""
import logging
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from .models import SuspiciousActivity, AIResponseAlert, AIUsageLog
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDay
from recommendations.models import Recommendation

logger = logging.getLogger(__name__)


def _get_severity_badge(severity):
    """Retorna badge HTML colorido para a severidade."""
    colors = {
        'low': ('#ffc107', '#000', '🟡'),
        'medium': ('#fd7e14', '#fff', '🟠'),
        'high': ('#dc3545', '#fff', '🔴'),
        'critical': ('#6f42c1', '#fff', '🚨'),
    }
    color, text_color, emoji = colors.get(severity, ('#6c757d', '#fff', '⚪'))
    label = dict(SuspiciousActivity.SEVERITY_LEVELS).get(severity, severity)
    return format_html(
        '<span style="background:{};color:{};padding:2px 8px;border-radius:12px;'
        'font-size:0.8em;font-weight:bold;">{} {}</span>',
        color, text_color, emoji, label
    )


# ==============================================================================
# AÇÕES EM MASSA
# ==============================================================================

def action_mark_reviewed(modeladmin, request, queryset):
    """Marca atividades selecionadas como revisadas."""
    count = queryset.filter(reviewed=False).update(
        reviewed=True,
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
        action_taken='none',
    )
    messages.success(request, f"✅ {count} atividade(s) marcada(s) como revisada(s).")


action_mark_reviewed.short_description = "✅ Marcar como Revisado"


def action_send_whatsapp(modeladmin, request, queryset):
    """Envia alerta WhatsApp manualmente para os registros selecionados."""
    from .tasks import dispatch_whatsapp_alert

    count = 0
    for obj in queryset:
        if isinstance(obj, SuspiciousActivity):
            dispatch_whatsapp_alert(activity_id=obj.pk)
        elif isinstance(obj, AIResponseAlert):
            dispatch_whatsapp_alert(ai_alert_id=obj.pk)
        count += 1

    messages.info(request, f"📱 {count} alerta(s) WhatsApp enfileirado(s) para envio.")


action_send_whatsapp.short_description = "📱 Enviar Alerta WhatsApp"


def action_mark_resolved(modeladmin, request, queryset):
    """Marca alertas de IA selecionados como resolvidos."""
    count = queryset.filter(resolved=False).update(
        resolved=True,
        resolved_by=request.user,
        resolved_at=timezone.now(),
    )
    messages.success(request, f"✅ {count} alerta(s) marcado(s) como resolvido(s).")


action_mark_resolved.short_description = "✅ Marcar como Resolvido"


# ==============================================================================
# ADMIN: SUSPICIOUS ACTIVITY
# ==============================================================================

@admin.register(SuspiciousActivity)
class SuspiciousActivityAdmin(admin.ModelAdmin):
    """
    Painel admin para gerenciar atividades suspeitas de usuários.
    """
    list_display = [
        'created_at_display',
        'severity_badge',
        'activity_type_display',
        'user_display',
        'message_preview',
        'keywords_display',
        'alert_status',
        'review_status',
    ]
    list_filter = [
        'severity',
        'activity_type',
        'reviewed',
        'alert_sent',
        'action_taken',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = [
        'user__username',
        'user__email',
        'message_content',
        'user_ip',
        'reviewer_notes',
    ]
    readonly_fields = [
        'created_at',
        'alert_sent_at',
        'reviewed_at',
        'message_link',
        'session_link',
        'severity_badge_detail',
        'user_history_link',
    ]
    fieldsets = [
        ('📋 Informações da Ocorrência', {
            'fields': [
                'created_at',
                'activity_type',
                'severity_badge_detail',
                'message_content',
                'detected_keywords',
            ]
        }),
        ('👤 Usuário', {
            'fields': [
                'user',
                'user_history_link',
                'session',
                'session_link',
                'message_link',
                'user_ip',
                'session_key',
            ]
        }),
        ('📱 Alerta WhatsApp', {
            'fields': [
                'alert_sent',
                'alert_sent_at',
            ]
        }),
        ('✅ Revisão', {
            'fields': [
                'reviewed',
                'reviewed_by',
                'reviewed_at',
                'action_taken',
                'reviewer_notes',
            ]
        }),
    ]
    actions = [action_mark_reviewed, action_send_whatsapp]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25

    # ---- Campos calculados para list_display ----

    @admin.display(description='Detectado em', ordering='created_at')
    def created_at_display(self, obj):
        local = timezone.localtime(obj.created_at)
        return format_html(
            '<span title="{}">{}</span>',
            local.strftime('%d/%m/%Y %H:%M:%S'),
            local.strftime('%d/%m %H:%M'),
        )

    @admin.display(description='Severidade', ordering='severity')
    def severity_badge(self, obj):
        return _get_severity_badge(obj.severity)

    @admin.display(description='Tipo')
    def activity_type_display(self, obj):
        icons = {
            'abusive_language': '🤬',
            'spam': '📨',
            'jailbreak_attempt': '🔓',
            'illegal_content': '⛔',
            'harassment': '😡',
            'personal_data_solicitation': '🔍',
            'other': '❓',
        }
        icon = icons.get(obj.activity_type, '❓')
        return format_html('{} {}', icon, obj.get_activity_type_display())

    @admin.display(description='Usuário', ordering='user__username')
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.pk, obj.user.username
            )
        return format_html('<em style="color:#999;">Anônimo ({})</em>', obj.user_ip or obj.session_key or 'desconhecido')

    @admin.display(description='Mensagem')
    def message_preview(self, obj):
        preview = obj.message_content[:80]
        if len(obj.message_content) > 80:
            preview += '...'
        return format_html('<span title="{}">{}</span>', obj.message_content, preview)

    @admin.display(description='Palavras Detectadas')
    def keywords_display(self, obj):
        if obj.detected_keywords:
            kws = ', '.join(str(k) for k in obj.detected_keywords[:3])
            return format_html('<code style="font-size:0.8em;">{}</code>', kws)
        return '—'

    @admin.display(description='WhatsApp')
    def alert_status(self, obj):
        if obj.alert_sent:
            local = timezone.localtime(obj.alert_sent_at)
            return format_html(
                '<span style="color:green;" title="Enviado em {}">✅ Enviado</span>',
                local.strftime('%d/%m %H:%M') if obj.alert_sent_at else '—'
            )
        return format_html('<span style="color:#dc3545;">⏳ Pendente</span>')

    @admin.display(description='Revisão')
    def review_status(self, obj):
        if obj.reviewed:
            return format_html('<span style="color:green;">✅ Revisado</span>')
        return format_html('<span style="color:#dc3545;font-weight:bold;">🔴 Pendente</span>')

    # ---- Campos readonly no detalhe ----

    @admin.display(description='Severidade')
    def severity_badge_detail(self, obj):
        return _get_severity_badge(obj.severity)

    @admin.display(description='Ver Mensagem no Admin')
    def message_link(self, obj):
        if obj.message:
            return format_html(
                '<a href="/admin/chatbot_literario/chatmessage/{}/change/" target="_blank">'
                '🔗 Mensagem #{}</a>',
                obj.message.pk, obj.message.pk
            )
        return '—'

    @admin.display(description='Ver Sessão no Admin')
    def session_link(self, obj):
        if obj.session:
            return format_html(
                '<a href="/admin/chatbot_literario/chatsession/{}/change/" target="_blank">'
                '🔗 Sessão #{}</a>',
                obj.session.pk, obj.session.pk
            )
        return '—'

    @admin.display(description='Histórico do Usuário')
    def user_history_link(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/monitoring/suspiciousactivity/?user__id__exact={}" target="_blank">'
                '🔍 Ver todos os alertas deste usuário</a>',
                obj.user.pk
            )
        return '—'


# ==============================================================================
# ADMIN: AI RESPONSE ALERT
# ==============================================================================

@admin.register(AIResponseAlert)
class AIResponseAlertAdmin(admin.ModelAdmin):
    """
    Painel admin para gerenciar alertas de problemas nas respostas da IA.
    """
    list_display = [
        'created_at_display',
        'severity_badge',
        'alert_type_display',
        'provider_badge',
        'user_display',
        'complaint_preview',
        'response_preview_short',
        'alert_status',
        'resolution_status',
    ]
    list_filter = [
        'severity',
        'alert_type',
        'provider',
        'resolved',
        'alert_sent',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = [
        'user__username',
        'user__email',
        'user_complaint_text',
        'ai_response_preview',
        'error_message',
        'resolution_notes',
    ]
    readonly_fields = [
        'created_at',
        'alert_sent_at',
        'resolved_at',
        'message_link',
        'session_link',
        'severity_badge_detail',
    ]
    fieldsets = [
        ('📋 Informações do Alerta', {
            'fields': [
                'created_at',
                'alert_type',
                'severity_badge_detail',
                'provider',
            ]
        }),
        ('👤 Usuário e Sessão', {
            'fields': [
                'user',
                'session',
                'session_link',
                'message',
                'message_link',
            ]
        }),
        ('💬 Detalhes do Problema', {
            'fields': [
                'user_complaint_text',
                'ai_response_preview',
                'error_message',
            ]
        }),
        ('📱 Alerta WhatsApp', {
            'fields': [
                'alert_sent',
                'alert_sent_at',
            ]
        }),
        ('✅ Resolução', {
            'fields': [
                'resolved',
                'resolved_by',
                'resolved_at',
                'resolution_notes',
            ]
        }),
    ]
    actions = [action_mark_resolved, action_send_whatsapp]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25

    @admin.display(description='Criado em', ordering='created_at')
    def created_at_display(self, obj):
        local = timezone.localtime(obj.created_at)
        return format_html(
            '<span title="{}">{}</span>',
            local.strftime('%d/%m/%Y %H:%M:%S'),
            local.strftime('%d/%m %H:%M'),
        )

    @admin.display(description='Severidade', ordering='severity')
    def severity_badge(self, obj):
        return _get_severity_badge(obj.severity)

    @admin.display(description='Tipo de Alerta')
    def alert_type_display(self, obj):
        icons = {
            'user_complaint': '💬',
            'negative_feedback': '👎',
            'api_error': '🛠️',
            'timeout': '⏱️',
            'empty_response': '📭',
            'hallucination_suspected': '🌀',
            'quota_exceeded': '📊',
            'content_filter': '🚫',
            'other': '❓',
        }
        icon = icons.get(obj.alert_type, '❓')
        return format_html('{} {}', icon, obj.get_alert_type_display())

    @admin.display(description='Provedor IA', ordering='provider')
    def provider_badge(self, obj):
        colors = {
            'gemini': ('#4285f4', '#fff'),
            'groq': ('#f55036', '#fff'),
            'unknown': ('#6c757d', '#fff'),
        }
        color, text_color = colors.get(obj.provider, ('#6c757d', '#fff'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:12px;'
            'font-size:0.8em;font-weight:bold;">{}</span>',
            color, text_color, obj.get_provider_display()
        )

    @admin.display(description='Usuário', ordering='user__username')
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.pk, obj.user.username
            )
        return format_html('<em style="color:#999;">Anônimo</em>')

    @admin.display(description='Reclamação')
    def complaint_preview(self, obj):
        if obj.user_complaint_text:
            preview = obj.user_complaint_text[:60]
            if len(obj.user_complaint_text) > 60:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.user_complaint_text, preview)
        return format_html('<em style="color:#999;">—</em>')

    @admin.display(description='Resposta IA')
    def response_preview_short(self, obj):
        if obj.ai_response_preview:
            preview = obj.ai_response_preview[:60]
            if len(obj.ai_response_preview) > 60:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.ai_response_preview, preview)
        return format_html('<em style="color:#999;">—</em>')

    @admin.display(description='WhatsApp')
    def alert_status(self, obj):
        if obj.alert_sent:
            local = timezone.localtime(obj.alert_sent_at) if obj.alert_sent_at else None
            return format_html(
                '<span style="color:green;" title="{}">✅ Enviado</span>',
                local.strftime('%d/%m %H:%M') if local else '—'
            )
        return format_html('<span style="color:#dc3545;">⏳ Pendente</span>')

    @admin.display(description='Status')
    def resolution_status(self, obj):
        if obj.resolved:
            return format_html('<span style="color:green;">✅ Resolvido</span>')
        return format_html('<span style="color:#dc3545;font-weight:bold;">🔴 Aberto</span>')

    @admin.display(description='Severidade')
    def severity_badge_detail(self, obj):
        return _get_severity_badge(obj.severity)

    @admin.display(description='Ver Mensagem no Admin')
    def message_link(self, obj):
        if obj.message:
            return format_html(
                '<a href="/admin/chatbot_literario/chatmessage/{}/change/" target="_blank">'
                '🔗 Mensagem #{}</a>',
                obj.message.pk, obj.message.pk
            )
        return '—'

    @admin.display(description='Ver Sessão no Admin')
    def session_link(self, obj):
        if obj.session:
            return format_html(
                '<a href="/admin/chatbot_literario/chatsession/{}/change/" target="_blank">'
                '🔗 Sessão #{}</a>',
                obj.session.pk, obj.session.pk
            )
        return '—'


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    """
    Painel admin para telemetria de uso, tokens e custos da Inteligência Artificial.
    """
    list_display = (
        'created_at_display',
        'feature_name_display',
        'provider_badge',
        'model_name',
        'tokens_summary',
        'estimated_cost_display',
        'response_time_seconds_display',
        'status_badge'
    )
    list_filter = (
        'provider',
        'feature_name',
        'status',
        'created_at'
    )
    search_fields = (
        'feature_name',
        'provider',
        'model_name',
        'user__username',
        'error_message'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    readonly_fields = (
        'created_at', 'user', 'feature_name', 'provider', 'model_name', 
        'prompt_tokens', 'completion_tokens', 'total_tokens', 
        'estimated_cost', 'response_time_seconds', 'status', 'error_message'
    )

    def has_add_permission(self, request):
        """Impedir inserções manuais."""
        return False

    @admin.display(description='Data/Hora')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M:%S')

    @admin.display(description='Funcionalidade')
    def feature_name_display(self, obj):
        features = {
            'chatbot': '💬 Chatbot/Assistente',
            'recommendations': '📚 Recomendações',
            'book_review': '📝 Resenha de IA',
            'reader_profile': '👤 Perfil Literário',
            'news_generation': '📰 Notícias/Artigos',
            'general': '⚙️ Geral'
        }
        return features.get(obj.feature_name, obj.feature_name.upper())

    @admin.display(description='Provedor')
    def provider_badge(self, obj):
        colors = {
            'gemini': '#4285f4',
            'groq': '#f55f44',
            'openai': '#10a37f',
            'claude': '#d97706',
            'local': '#6b7280',
            'mock': '#6c757d'
        }
        color = colors.get(obj.provider, '#000')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;'
            'font-size:0.85em;font-weight:bold;">{}</span>',
            color, obj.provider.upper()
        )

    @admin.display(description='Tokens (P / R / T)')
    def tokens_summary(self, obj):
        return f"{obj.prompt_tokens} / {obj.completion_tokens} / {obj.total_tokens}"

    @admin.display(description='Custo')
    def estimated_cost_display(self, obj):
        return f"${obj.estimated_cost:.5f}"

    @admin.display(description='Latência')
    def response_time_seconds_display(self, obj):
        return f"{obj.response_time_seconds:.2f}s"

    @admin.display(description='Status')
    def status_badge(self, obj):
        if obj.status == 'success':
            return format_html('<span style="color:green;font-weight:bold;">✅ Sucesso</span>')
        return format_html('<span style="color:red;font-weight:bold;" title="{}">❌ Falha</span>', obj.error_message[:200])

    def changelist_view(self, request, extra_context=None):
        """Injeta agregados estatísticos dinâmicos para renderizar o Dashboard de IA."""
        response = super().changelist_view(request, extra_context=extra_context)
        
        if hasattr(response, 'context_data'):
            cl = response.context_data['cl']
            queryset = cl.get_queryset(request)
            
            # 1. Agregados para KPIs
            aggregates = queryset.aggregate(
                total_calls=Count('id'),
                total_prompt=Sum('prompt_tokens'),
                total_completion=Sum('completion_tokens'),
                total_toks=Sum('total_tokens'),
                total_cst=Sum('estimated_cost'),
                avg_lat=Avg('response_time_seconds')
            )
            
            total_calls = aggregates['total_calls'] or 0
            total_tokens = aggregates['total_toks'] or 0
            total_cost = aggregates['total_cst'] or 0.0
            avg_latency = aggregates['avg_lat'] or 0.0
            
            success_count = queryset.filter(status='success').count()
            success_rate = round((success_count / total_calls * 100), 1) if total_calls > 0 else 0.0
            
            stats_summary = {
                'total_calls': total_calls,
                'total_tokens': f"{total_tokens:,}",
                'total_cost': f"${total_cost:,.4f}",
                'avg_latency': f"{avg_latency:.2f}s",
                'success_rate': success_rate
            }
            
            # 2. Dados para Gráficos
            # A. Consumo diário (últimos 30 dias)
            daily_usage = list(reversed(
                queryset.annotate(day=TruncDay('created_at'))
                .values('day')
                .annotate(tokens=Sum('total_tokens'), cost=Sum('estimated_cost'))
                .order_by('-day')[:30]
            ))
            
            # B. Tokens por Provedor
            tokens_by_provider = list(
                queryset.values('provider')
                .annotate(tokens=Sum('total_tokens'))
                .order_by('-tokens')
            )
            
            # C. Custo por Provedor
            cost_by_provider = list(
                queryset.values('provider')
                .annotate(cost=Sum('estimated_cost'))
                .order_by('-cost')
            )
            
            # D. Chamadas por Feature
            calls_by_feature = list(
                queryset.values('feature_name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # E. Latência Média por Provedor
            latency_by_provider = list(
                queryset.values('provider')
                .annotate(latency=Avg('response_time_seconds'))
                .order_by('-latency')
            )
            
            # F. CTR de Recomendações de IA
            ai_recs = Recommendation.objects.filter(recommendation_type='ai')
            total_ai_recs = ai_recs.count()
            clicked_ai_recs = ai_recs.filter(is_clicked=True).count()
            ctr = round((clicked_ai_recs / total_ai_recs * 100), 1) if total_ai_recs > 0 else 0.0
            
            # G. Alertas / Feedbacks Negativos
            total_alerts = AIResponseAlert.objects.filter(alert_type__in=['user_complaint', 'negative_feedback']).count()
            neg_feedback_rate = round((total_alerts / max(1, success_count) * 100), 2)
            
            chart_data = {
                'daily': {
                    'labels': [c['day'].strftime('%d/%m') if c['day'] else '' for c in daily_usage],
                    'tokens': [c['tokens'] or 0 for c in daily_usage],
                    'cost': [float(c['cost'] or 0.0) for c in daily_usage]
                },
                'provider_tokens': {
                    'labels': [p['provider'].upper() for p in tokens_by_provider],
                    'values': [p['tokens'] or 0 for p in tokens_by_provider]
                },
                'provider_cost': {
                    'labels': [p['provider'].upper() for p in cost_by_provider],
                    'values': [float(p['cost'] or 0.0) for p in cost_by_provider]
                },
                'feature_calls': {
                    'labels': [f['feature_name'].upper() for f in calls_by_feature],
                    'values': [f['count'] for f in calls_by_feature]
                },
                'provider_latency': {
                    'labels': [p['provider'].upper() for p in latency_by_provider],
                    'values': [round(p['latency'] or 0.0, 2) for p in latency_by_provider]
                },
                'recommendation_ctr': {
                    'labels': ['Clicadas (CTR)', 'Não Clicadas'],
                    'values': [clicked_ai_recs, max(0, total_ai_recs - clicked_ai_recs)],
                    'ctr': ctr
                },
                'satisfaction': {
                    'labels': ['Feedbacks Negativos', 'Sucesso (Sem Alertas)'],
                    'values': [total_alerts, max(0, success_count - total_alerts)],
                    'rate': neg_feedback_rate
                }
            }
            
            extra_context = extra_context or {}
            extra_context['chart_data'] = chart_data
            extra_context['stats_summary'] = stats_summary
            
            response.context_data.update(extra_context)
            
        return response


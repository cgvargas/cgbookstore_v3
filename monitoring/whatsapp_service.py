"""
Serviço de notificações via WhatsApp usando CallMeBot.

CallMeBot é uma API gratuita que permite enviar mensagens WhatsApp
sem necessidade de servidores extras.

SETUP (5 minutos):
1. Salve o número +34644001121 nos seus contatos do WhatsApp
2. Envie para ele a mensagem: "I allow callmebot to send me messages"
3. Aguarde receber sua API KEY por WhatsApp
4. Configure no .env:
   WHATSAPP_ADMIN_NUMBER=55119XXXXXXXX  (com código do país, sem +)
   CALLMEBOT_API_KEY=XXXXXXXX           (key recebida)

Documentação: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""
import logging
import urllib.parse
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """
    Serviço de envio de alertas via WhatsApp (CallMeBot).

    Envia mensagens formatadas para o administrador do sistema
    quando atividades suspeitas ou erros de IA são detectados.
    """

    CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"
    REQUEST_TIMEOUT = 10  # segundos

    def __init__(self):
        self.phone = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '')
        self.api_key = getattr(settings, 'CALLMEBOT_API_KEY', '')
        self.enabled = bool(self.phone and self.api_key)

        if not self.enabled:
            logger.warning(
                "⚠️ WhatsApp não configurado. "
                "Configure WHATSAPP_ADMIN_NUMBER e CALLMEBOT_API_KEY no .env"
            )

    def _send_message(self, text: str) -> bool:
        """
        Envia uma mensagem WhatsApp via CallMeBot.

        Args:
            text: Texto da mensagem (suporta *negrito* e _itálico_)

        Returns:
            True se enviado com sucesso, False caso contrário.
        """
        if not self.enabled:
            logger.warning("WhatsApp desabilitado: credenciais não configuradas.")
            return False

        try:
            # CallMeBot aceita texto URL-encoded via GET
            encoded_text = urllib.parse.quote(text)
            url = f"{self.CALLMEBOT_URL}?phone={self.phone}&text={encoded_text}&apikey={self.api_key}"

            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
            response_text = response.text

            # CallMeBot costuma retornar HTTP 200 mesmo em caso de erro, com a mensagem de erro no corpo.
            # Sucesso contém "queued" ou "success" ou "enviado"
            is_success = response.status_code == 200 and any(
                word in response_text.lower() for word in ["queued", "success", "enviado", "created"]
            )

            if is_success:
                logger.info(f"✅ WhatsApp enviado com sucesso para {self.phone}. Resposta da API: {response_text.strip()}")
                return True
            else:
                logger.error(
                    f"❌ Falha ao enviar WhatsApp. Status HTTP: {response.status_code} | "
                    f"Resposta da API: {response_text.strip()}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao enviar mensagem WhatsApp via CallMeBot")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Erro de conexão ao enviar WhatsApp: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao enviar WhatsApp: {e}", exc_info=True)
            return False

    def send_suspicious_activity_alert(self, activity) -> bool:
        """
        Envia alerta de atividade suspeita de usuário.

        Args:
            activity: Instância de SuspiciousActivity

        Returns:
            True se enviado com sucesso.
        """
        now = timezone.localtime(activity.created_at)
        user_label = (
            f"{activity.user.username} (ID: {activity.user.pk})"
            if activity.user
            else f"Anônimo (IP: {activity.user_ip or 'desconhecido'})"
        )

        # Preview da mensagem (max 150 chars)
        msg_preview = activity.message_content[:150]
        if len(activity.message_content) > 150:
            msg_preview += '...'

        # Palavras detectadas
        keywords_str = ', '.join(activity.detected_keywords[:5]) if activity.detected_keywords else 'N/A'

        text = (
            f"{activity.severity_emoji} *ALERTA - Conduta Suspeita* {activity.severity_emoji}\n\n"
            f"📋 *Tipo:* {activity.get_activity_type_display()}\n"
            f"⚠️ *Severidade:* {activity.get_severity_display().upper()}\n"
            f"👤 *Usuário:* {user_label}\n"
            f"💬 *Mensagem:* _{msg_preview}_\n"
            f"🔑 *Detectado:* {keywords_str}\n"
            f"🕐 *Horário:* {now.strftime('%d/%m/%Y às %H:%M')}\n\n"
            f"🔗 Revisar: {activity.admin_url}"
        )

        success = self._send_message(text)
        if success:
            activity.mark_alert_sent()
        return success

    def send_ai_error_alert(self, alert) -> bool:
        """
        Envia alerta de problema na resposta da IA.

        Args:
            alert: Instância de AIResponseAlert

        Returns:
            True se enviado com sucesso.
        """
        now = timezone.localtime(alert.created_at)
        user_label = (
            f"{alert.user.username} (ID: {alert.user.pk})"
            if alert.user
            else 'Anônimo'
        )

        # Preview da resposta (max 120 chars)
        response_preview = ''
        if alert.ai_response_preview:
            response_preview = alert.ai_response_preview[:120]
            if len(alert.ai_response_preview) > 120:
                response_preview += '...'

        # Texto da reclamação (max 120 chars)
        complaint_preview = ''
        if alert.user_complaint_text:
            complaint_preview = alert.user_complaint_text[:120]
            if len(alert.user_complaint_text) > 120:
                complaint_preview += '...'

        # Montar corpo da mensagem
        lines = [
            f"{alert.severity_emoji} *ALERTA - Problema na IA* {alert.severity_emoji}\n",
            f"📋 *Tipo:* {alert.get_alert_type_display()}",
            f"⚠️ *Severidade:* {alert.get_severity_display().upper()}",
            f"🤖 *Provedor:* {alert.get_provider_display()}",
            f"👤 *Usuário:* {user_label}",
        ]

        if complaint_preview:
            lines.append(f"💬 *Reclamação:* _{complaint_preview}_")

        if response_preview:
            lines.append(f"📝 *Resposta IA:* _{response_preview}_")

        if alert.error_message:
            err_preview = alert.error_message[:100]
            lines.append(f"🛠️ *Erro técnico:* `{err_preview}`")

        lines.append(f"🕐 *Horário:* {now.strftime('%d/%m/%Y às %H:%M')}")
        lines.append(f"\n🔗 Resolver: {alert.admin_url}")

        text = '\n'.join(lines)
        success = self._send_message(text)
        if success:
            alert.mark_alert_sent()
        return success

    def send_daily_summary(self, stats: dict) -> bool:
        """
        Envia resumo diário de monitoramento.

        Args:
            stats: Dicionário com estatísticas do dia
              {
                'date': '29/05/2026',
                'suspicious_total': 3,
                'suspicious_critical': 1,
                'suspicious_high': 1,
                'suspicious_unreviewed': 0,
                'ai_alerts_total': 12,
                'ai_alerts_critical': 2,
                'ai_alerts_unresolved': 5,
              }

        Returns:
            True se enviado com sucesso.
        """
        date_str = stats.get('date', timezone.now().strftime('%d/%m/%Y'))
        suspicious_total = stats.get('suspicious_total', 0)
        suspicious_critical = stats.get('suspicious_critical', 0)
        suspicious_high = stats.get('suspicious_high', 0)
        suspicious_unreviewed = stats.get('suspicious_unreviewed', 0)
        ai_total = stats.get('ai_alerts_total', 0)
        ai_critical = stats.get('ai_alerts_critical', 0)
        ai_unresolved = stats.get('ai_alerts_unresolved', 0)

        # Ícone de status geral
        if suspicious_critical > 0 or ai_critical > 0:
            status_icon = '🚨 Requer atenção imediata!'
        elif suspicious_total > 5 or ai_total > 10:
            status_icon = '⚠️ Dia agitado — verifique o admin'
        else:
            status_icon = '✅ Tudo sob controle'

        text = (
            f"📊 *Resumo Diário — {date_str}*\n\n"
            f"🔍 *Condutas Suspeitas:*\n"
            f"  • Total: {suspicious_total} ocorrências\n"
            f"  • Críticas: {suspicious_critical} | Altas: {suspicious_high}\n"
            f"  • Não revisadas: {suspicious_unreviewed}\n\n"
            f"🤖 *Qualidade da IA:*\n"
            f"  • Total de alertas: {ai_total}\n"
            f"  • Críticos: {ai_critical}\n"
            f"  • Não resolvidos: {ai_unresolved}\n\n"
            f"{status_icon}\n\n"
            f"🔗 Admin: {getattr(settings, 'SITE_URL', '')}/admin/monitoring/"
        )

        return self._send_message(text)

    def send_test_message(self) -> bool:
        """Envia mensagem de teste para validar configuração."""
        now = timezone.localtime(timezone.now())
        text = (
            f"✅ *CG.BookStore — Teste de Alerta*\n\n"
            f"Sistema de monitoramento configurado com sucesso!\n"
            f"🕐 {now.strftime('%d/%m/%Y às %H:%M')}\n\n"
            f"Você receberá alertas aqui quando:\n"
            f"• Detectar conduta suspeita de usuários\n"
            f"• Ocorrer erro nas respostas da IA\n"
            f"• Usuário reclamar de uma resposta"
        )
        return self._send_message(text)


# Instância global reutilizável (padrão singleton)
_notifier_instance = None


def get_whatsapp_notifier() -> WhatsAppNotifier:
    """Retorna instância singleton do WhatsAppNotifier."""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = WhatsAppNotifier()
    return _notifier_instance

"""
Brevo (Sendinblue) Email Backend for Django
Usa a API REST do Brevo para entrega confiável de emails.

REQUISITO: O IP do servidor deve estar autorizado no painel do Brevo.
  Brevo > Configurações > Segurança > IPs Autorizados
  URL: https://app.brevo.com/security/authorised_ips

Configurar no .env:
  USE_BREVO_API=True
  BREVO_API_KEY=xkeysib-...
  DEFAULT_FROM_EMAIL=seu@email.com
  CONTACT_EMAIL=destino@email.com
"""
import os
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)


class BrevoBackend(BaseEmailBackend):
    """
    Email backend que usa a API REST do Brevo (Sendinblue).
    Mais confiável que SMTP para Render Free tier.

    NOTA: Requer que o IP do servidor esteja autorizado em:
    https://app.brevo.com/security/authorised_ips
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        # Tentar pegar API key de várias fontes
        self.api_key = (
            getattr(settings, 'BREVO_API_KEY', None) or
            os.environ.get('BREVO_API_KEY') or
            os.environ.get('EMAIL_HOST_PASSWORD')
        )
        self.client = None
        if not self.api_key:
            logger.warning("⚠️ BrevoBackend: BREVO_API_KEY não configurada!")

    def open(self):
        """Initialize Brevo client"""
        if self.client:
            return False
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.client = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
            logger.debug("✅ Brevo API client inicializado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Brevo client: {e}")
            if not self.fail_silently:
                raise
            return False

    def close(self):
        """Close connection (not needed for HTTP API)"""
        self.client = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0

        if not self.client:
            self.open()

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"❌ Falha ao enviar email via Brevo: {e}")
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, email_message):
        """Send a single EmailMessage object"""
        if not email_message.recipients():
            return False

        from_email = email_message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        to_emails = email_message.recipients()

        # Prepare email data
        sender = {"email": from_email}
        to = [{"email": email} for email in to_emails]

        # Reply-To header
        reply_to = None
        extra_headers = getattr(email_message, 'extra_headers', {})
        if 'Reply-To' in extra_headers:
            reply_to = {"email": extra_headers['Reply-To']}

        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject=email_message.subject,
            reply_to=reply_to,
        )

        # Add content (HTML or plain text)
        if email_message.content_subtype == 'html':
            send_smtp_email.html_content = email_message.body
            for alt in email_message.alternatives:
                if alt[1] == 'text/plain':
                    send_smtp_email.text_content = alt[0]
        else:
            send_smtp_email.text_content = email_message.body
            for alt in email_message.alternatives:
                if alt[1] == 'text/html':
                    send_smtp_email.html_content = alt[0]

        try:
            api_response = self.client.send_transac_email(send_smtp_email)
            logger.info(
                f"✅ Email enviado via Brevo: '{email_message.subject}' "
                f"para {to_emails} | message_id={api_response.message_id}"
            )
            return api_response.message_id is not None
        except ApiException as e:
            logger.error(
                f"❌ Brevo ApiException ao enviar '{email_message.subject}': "
                f"status={e.status} body={e.body}"
            )
            if not self.fail_silently:
                raise
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado no Brevo backend: {e}")
            if not self.fail_silently:
                raise
            return False

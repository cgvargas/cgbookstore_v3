"""
Brevo (Sendinblue) Email Backend for Django
Uses Brevo's API for reliable email delivery
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


class BrevoBackend(BaseEmailBackend):
    """
    Email backend that uses Brevo's (Sendinblue) API.
    More reliable than SendGrid for Render Free tier.
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

    def open(self):
        """Initialize Brevo client"""
        if self.client:
            return False
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.client = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            return True
        except Exception:
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
            except Exception:
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, email_message):
        """Send a single EmailMessage object"""
        if not email_message.recipients():
            return False

        from_email = email_message.from_email or os.environ.get('DEFAULT_FROM_EMAIL')
        to_emails = email_message.recipients()

        # Prepare email data
        sender = {"email": from_email}
        to = [{"email": email} for email in to_emails]

        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject=email_message.subject,
        )

        # Add content (HTML or plain text)
        if email_message.content_subtype == 'html':
            send_smtp_email.html_content = email_message.body
            # Add plain text alternative if available
            for alt in email_message.alternatives:
                if alt[1] == 'text/plain':
                    send_smtp_email.text_content = alt[0]
        else:
            send_smtp_email.text_content = email_message.body
            # Add HTML alternative if available
            for alt in email_message.alternatives:
                if alt[1] == 'text/html':
                    send_smtp_email.html_content = alt[0]

        try:
            api_response = self.client.send_transac_email(send_smtp_email)
            return api_response.message_id is not None
        except ApiException as e:
            if not self.fail_silently:
                raise
            return False
        except Exception as e:
            if not self.fail_silently:
                raise
            return False

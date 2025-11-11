"""
SendGrid Web API Email Backend for Django
Uses HTTP/HTTPS instead of SMTP to bypass firewall restrictions
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendGridBackend(BaseEmailBackend):
    """
    Email backend that uses SendGrid's Web API instead of SMTP.
    This bypasses port 587 firewall restrictions on Render Free tier.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.environ.get('SENDGRID_API_KEY') or os.environ.get('EMAIL_HOST_PASSWORD')
        self.client = None

    def open(self):
        """Initialize SendGrid client"""
        if self.client:
            return False
        try:
            self.client = SendGridAPIClient(self.api_key)
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

        # Create the email
        message = Mail(
            from_email=Email(from_email),
            to_emails=[To(email) for email in to_emails],
            subject=email_message.subject,
        )

        # Add content (HTML or plain text)
        if email_message.content_subtype == 'html':
            # HTML email
            message.content = Content("text/html", email_message.body)
            # Add plain text alternative if available
            for alt in email_message.alternatives:
                if alt[1] == 'text/plain':
                    message.content = [
                        Content("text/plain", alt[0]),
                        Content("text/html", email_message.body)
                    ]
        else:
            # Plain text email
            message.content = Content("text/plain", email_message.body)
            # Add HTML alternative if available
            for alt in email_message.alternatives:
                if alt[1] == 'text/html':
                    message.content = [
                        Content("text/plain", email_message.body),
                        Content("text/html", alt[0])
                    ]

        try:
            response = self.client.send(message)
            return response.status_code in [200, 202]
        except Exception as e:
            if not self.fail_silently:
                raise
            return False

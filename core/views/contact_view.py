# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\contact_view.py

import logging
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.core.mail import EmailMessage as DjangoEmailMessage
from django.conf import settings

from core.utils.anti_bot import (
    generate_bot_token,
    validate_bot_token,
    is_disposable_email,
    check_rate_limit,
)

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    """
    Formulário de contato com envio de email e categorização de assuntos (incluindo Direitos Autorais/Takedown).
    Inclui proteção anti-bot com honeypot e time-gate criptográfico.
    """
    CATEGORY_CHOICES = [
        ('general', 'Dúvidas Gerais / Atendimento'),
        ('support', 'Suporte Técnico / Acesso'),
        ('feedback', 'Sugestões e Elogios'),
        ('partnership', 'Parcerias e Editoras'),
        ('copyright_takedown', '🛡️ Direitos Autorais / Solicitação de Remoção de Conteúdo (Takedown)'),
        ('other', 'Outro Assunto'),
    ]

    # Campos anti-bot
    website_hp = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'style': 'position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0; pointer-events: none;',
            'aria-hidden': 'true',
        })
    )
    bot_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    name = forms.CharField(
        max_length=100,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label='Categoria do Assunto',
        initial='general',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.CharField(
        max_length=200,
        label='Assunto Específico',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título ou identificação da mensagem/obra'})
    )
    message = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua mensagem detalhada aqui...',
            'rows': 5
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['bot_token'].initial = generate_bot_token()


class ContactView(FormView):
    """
    View para página de contato.
    Envia email via Brevo ao submeter o formulário após validação anti-bot.
    """
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        """
        Processa o formulário com filtragem anti-bot e envia email via Brevo.
        """
        name = form.cleaned_data['name']
        sender_email = form.cleaned_data['email']
        category_code = form.cleaned_data.get('category', 'general')
        category_label = dict(ContactForm.CATEGORY_CHOICES).get(category_code, category_code)
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Verificação de segurança Anti-Bot
        website_hp = form.cleaned_data.get('website_hp')
        bot_token = self.request.POST.get('bot_token') or form.cleaned_data.get('bot_token')
        is_valid_token, reason = validate_bot_token(bot_token, min_seconds=2.0)
        disposable = is_disposable_email(sender_email)
        allowed_rate = check_rate_limit(self.request, action='contact', max_attempts=5, window_seconds=600)

        # Se for identificado como bot ou abuso:
        if website_hp or not is_valid_token or disposable or not allowed_rate:
            logger.warning(
                f"[AntiBot Contact] Mensagem de SPAM descartada silenciosamente: "
                f"hp='{website_hp}', token_ok={is_valid_token} ({reason}), disposable={disposable}, "
                f"rate_ok={allowed_rate}, email={sender_email}, subject='{subject}'"
            )
            # Responde sucesso falso para despistar robôs sem enviar e-mail ao Brevo
            messages.success(
                self.request,
                'Mensagem enviada com sucesso! Entraremos em contato em breve. 📬'
            )
            return super().form_valid(form)

        # Prefixo de identificação administrativa prioritária
        prefix = "[DIREITOS AUTORAIS / TAKEDOWN]" if category_code == 'copyright_takedown' else "[CG.BookStore]"

        # Email de destino (quem recebe as mensagens de contato)
        contact_email = getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)

        # Corpo do email com todas as informações do remetente
        email_body = (
            f"Nova mensagem recebida pelo formulário de contato da CG.BookStore\n"
            f"{'=' * 60}\n\n"
            f"Categoria: {category_label}\n"
            f"Nome:      {name}\n"
            f"E-mail:    {sender_email}\n"
            f"Assunto:   {subject}\n\n"
            f"{'=' * 60}\n"
            f"Mensagem:\n\n"
            f"{message}\n\n"
            f"{'=' * 60}\n"
            f"Para responder, use o e-mail acima: {sender_email}\n"
        )

        try:
            email = DjangoEmailMessage(
                subject=f"{prefix} {subject}",
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact_email],
                reply_to=[f"{name} <{sender_email}>"],
            )
            email.send(fail_silently=False)
            logger.info(
                f"✅ Email de contato enviado com sucesso: '{subject}' de {sender_email}"
            )

            # Alerta Urgente via WhatsApp se for Direitos Autorais / Takedown
            if category_code == 'copyright_takedown':
                try:
                    from monitoring.whatsapp_service import get_whatsapp_notifier
                    notifier = get_whatsapp_notifier()
                    notifier.send_copyright_takedown_alert(
                        claimant_name=name,
                        claimant_email=sender_email,
                        subject=subject,
                        message=message,
                    )
                    logger.info("📲 Alerta urgente de Takedown enviado via WhatsApp para o administrador.")
                except Exception as wa_err:
                    logger.error(f"⚠️ Erro ao disparar alerta WhatsApp de takedown: {wa_err}", exc_info=True)

            messages.success(
                self.request,
                'Mensagem enviada com sucesso! Entraremos em contato em breve. 📬'
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email de contato: {e}", exc_info=True)
            messages.error(
                self.request,
                'Ocorreu um erro ao enviar sua mensagem. Tente novamente ou entre em contato '
                'diretamente pelo email: suporte@cgbookstore.com.br'
            )

        return super().form_valid(form)
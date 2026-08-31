# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\contact_view.py

import logging
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.core.mail import EmailMessage as DjangoEmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    """
    Formulário de contato com envio de email e categorização de assuntos (incluindo Direitos Autorais/Takedown).
    """
    CATEGORY_CHOICES = [
        ('general', 'Dúvidas Gerais / Atendimento'),
        ('support', 'Suporte Técnico / Acesso'),
        ('feedback', 'Sugestões e Elogios'),
        ('partnership', 'Parcerias e Editoras'),
        ('copyright_takedown', '🛡️ Direitos Autorais / Solicitação de Remoção de Conteúdo (Takedown)'),
        ('other', 'Outro Assunto'),
    ]

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


class ContactView(FormView):
    """
    View para página de contato.
    Envia email via Brevo ao submeter o formulário.
    """
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        """
        Processa o formulário e envia email via Brevo com destaque para comunicações de direitos autorais.
        """
        name = form.cleaned_data['name']
        sender_email = form.cleaned_data['email']
        category_code = form.cleaned_data.get('category', 'general')
        category_label = dict(ContactForm.CATEGORY_CHOICES).get(category_code, category_code)
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

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
            messages.success(
                self.request,
                'Mensagem enviada com sucesso! Entraremos em contato em breve. 📬'
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email de contato: {e}", exc_info=True)
            messages.error(
                self.request,
                'Ocorreu um erro ao enviar sua mensagem. Tente novamente ou entre em contato '
                'diretamente pelo email: cg.bookstore.online@outlook.com'
            )

        return super().form_valid(form)
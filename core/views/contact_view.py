# C:\Users\claud\OneDrive\ProjectsDjango\CGBookStore_v3\core\views\contact_view.py

from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms


class ContactForm(forms.Form):
    """
    Formulário de contato.
    Preparado para futura integração com envio de email.
    """
    name = forms.CharField(
        max_length=100,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    subject = forms.CharField(
        max_length=200,
        label='Assunto',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto da mensagem'})
    )
    message = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua mensagem aqui...',
            'rows': 5
        })
    )


class ContactView(FormView):
    """
    View para página de contato.
    Exibe formulário de contato (apenas visual por enquanto).
    Preparada para futura implementação de envio de email.
    """
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')

    def form_valid(self, form):
        """
        Processa o formulário quando válido.

        TODO: Implementar envio de email (Opção C)
        - Configurar SMTP no settings.py
        - Usar send_mail do Django
        - Adicionar template de email
        """
        # Por enquanto, apenas exibe mensagem de sucesso
        messages.success(
            self.request,
            'Mensagem recebida! Em breve entraremos em contato.'
        )

        # FUTURO: Descomentar para enviar email
        # from django.core.mail import send_mail
        # send_mail(
        #     subject=f"[CG.BookStore] {form.cleaned_data['subject']}",
        #     message=form.cleaned_data['message'],
        #     from_email=form.cleaned_data['email'],
        #     recipient_list=['contato@cgbookstore.com.br'],
        #     fail_silently=False,
        # )

        return super().form_valid(form)
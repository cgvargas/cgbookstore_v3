"""
Formulário customizado de cadastro com proteção anti-bot multicamadas.

Camadas de proteção:
1. Honeypot invisível (website_hp) - robôs preenchem, humanos não veem.
2. Time-Gate criptográfico (bot_token) - rejeita submissões instantâneas (< 2.5s).
3. Bloqueio de domínios descartáveis (besttempmail, tempmail, etc.).
4. Rate limiting por IP via cache.
"""
from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
import logging

from core.utils.anti_bot import (
    generate_bot_token,
    validate_bot_token,
    is_disposable_email,
    check_rate_limit,
)

logger = logging.getLogger(__name__)


class CustomSignupForm(SignupForm):
    """
    Extensão do SignupForm do Allauth com campos e validações anti-bot.
    """
    # Campo Honeypot - deve permanecer vazio
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
    
    # Token assinado com timestamp para medição do tempo de preenchimento
    bot_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se for exibição inicial do formulário, gera novo token com timestamp
        if not self.is_bound:
            self.fields['bot_token'].initial = generate_bot_token()

    def clean_website_hp(self):
        """Valida se o honeypot foi preenchido por um bot."""
        value = self.cleaned_data.get('website_hp')
        if value:
            logger.warning(f"[AntiBot Signup] Honeypot preenchido com: '{value}'")
            raise forms.ValidationError(_("Erro de validação do formulário. Por favor, tente novamente."))
        return value

    def clean_email(self):
        """Valida se o e-mail não pertence a um domínio descartável/temporário."""
        email = super().clean_email()
        if email and is_disposable_email(email):
            logger.warning(f"[AntiBot Signup] Tentativa com e-mail descartável bloqueada: {email}")
            raise forms.ValidationError(
                _("Endereços de e-mail temporários ou descartáveis não são permitidos. "
                  "Por favor, informe um e-mail válido permanente.")
            )
        return email

    def clean(self):
        """Validação global: Time-Gate e Rate Limit."""
        cleaned_data = super().clean()

        # 1. Validação de Time-Gate (Tempo mínimo de 2.5 segundos)
        token = self.data.get('bot_token') or cleaned_data.get('bot_token')
        is_valid, reason = validate_bot_token(token, min_seconds=2.5)
        if not is_valid:
            logger.warning(f"[AntiBot Signup] Time-gate falhou: {reason}")
            raise forms.ValidationError(_("Preenchimento rápido demais detectado. Por favor, aguarde alguns segundos e envie novamente."))

        # 2. Rate limiting por IP (máximo 4 cadastros por 10 minutos por IP)
        request = getattr(self, 'request', None)
        if not request:
            # Tenta recuperar request do adapter se disponível
            from allauth.account.adapter import get_adapter
            adapter = get_adapter()
            request = getattr(adapter, 'request', None)

        if request and not check_rate_limit(request, action='signup', max_attempts=4, window_seconds=600):
            raise forms.ValidationError(
                _("Muitas tentativas de cadastro recentes a partir deste endereço IP. "
                  "Por segurança, aguarde alguns minutos antes de tentar novamente.")
            )

        return cleaned_data

"""
Testes unitários para as defesas Anti-Bot em formulários públicos (Cadastro e Contato).
"""
import time
from django.test import TestCase, RequestFactory
from django.core import mail
from django.core.cache import cache
from core.utils.anti_bot import (
    generate_bot_token,
    validate_bot_token,
    is_disposable_email,
    check_rate_limit,
)
from accounts.forms_signup import CustomSignupForm
from core.views.contact_view import ContactForm, ContactView


class AntiBotUtilityTestCase(TestCase):
    """Testa os métodos utilitários anti-bot."""

    def test_disposable_email_detection(self):
        """Verifica a identificação de domínios descartáveis comuns."""
        self.assertTrue(is_disposable_email("spambot@besttempmail.com"))
        self.assertTrue(is_disposable_email("user@tempmail.com"))
        self.assertTrue(is_disposable_email("attacker@mailinator.com"))
        self.assertFalse(is_disposable_email("leitor@gmail.com"))
        self.assertFalse(is_disposable_email("cliente@outlook.com"))
        self.assertFalse(is_disposable_email("autor@cgbookstore.com.br"))

    def test_bot_token_validation_too_fast(self):
        """Tokens gerados imediatamente (< 2.5s) devem ser rejeitados."""
        token = generate_bot_token()
        is_valid, reason = validate_bot_token(token, min_seconds=2.5)
        self.assertFalse(is_valid)
        self.assertIn("rápida", reason.lower())

    def test_bot_token_validation_valid(self):
        """Tokens com tempo decorrido simulado devem ser aprovados."""
        # Simula token criado há 4 segundos
        from django.core import signing
        from core.utils.anti_bot import SALT_BOT_TOKEN
        past_payload = {'ts': time.time() - 4.0}
        valid_token = signing.dumps(past_payload, salt=SALT_BOT_TOKEN)

        is_valid, reason = validate_bot_token(valid_token, min_seconds=2.5)
        self.assertTrue(is_valid)
        self.assertEqual(reason, "OK")

    def test_bot_token_invalid_tampering(self):
        """Tokens forjados ou corrompidos devem falhar."""
        is_valid, reason = validate_bot_token("token_invalido_qualquer", min_seconds=2.5)
        self.assertFalse(is_valid)


class CustomSignupFormAntiBotTestCase(TestCase):
    """Testa a validação anti-bot do formulário de cadastro."""

    def setUp(self):
        cache.clear()
        from django.core import signing
        from core.utils.anti_bot import SALT_BOT_TOKEN
        # Gera um token simulando humano que demorou 5 segundos
        self.valid_human_token = signing.dumps({'ts': time.time() - 5.0}, salt=SALT_BOT_TOKEN)

    def test_honeypot_blocks_submission(self):
        """Se o campo honeypot for preenchido, a submissão deve ser bloqueada."""
        data = {
            'username': 'novoleitor',
            'email': 'novoleitor@gmail.com',
            'password1': 'SenhaForte@2026',
            'password2': 'SenhaForte@2026',
            'website_hp': 'http://spam-link.com',  # Honeypot preenchido por robô
            'bot_token': self.valid_human_token,
        }
        form = CustomSignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('website_hp', form.errors)

    def test_too_fast_submission_blocked(self):
        """Se o envio for instantâneo (robô em < 2.5s), deve bloquear."""
        instant_token = generate_bot_token()  # Gerado agora mesmo (0s)
        data = {
            'username': 'novoleitor2',
            'email': 'novoleitor2@gmail.com',
            'password1': 'SenhaForte@2026',
            'password2': 'SenhaForte@2026',
            'website_hp': '',
            'bot_token': instant_token,
        }
        form = CustomSignupForm(data=data)
        self.assertFalse(form.is_valid())
        # Deve ter erro non-field por tempo rápido
        self.assertTrue(len(form.non_field_errors()) > 0)

    def test_disposable_email_blocked(self):
        """Se o e-mail for de domínio descartável, deve bloquear."""
        data = {
            'username': 'novoleitor3',
            'email': 'hacker@besttempmail.com',
            'password1': 'SenhaForte@2026',
            'password2': 'SenhaForte@2026',
            'website_hp': '',
            'bot_token': self.valid_human_token,
        }
        form = CustomSignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_legitimate_human_signup_valid(self):
        """Usuário humano com e-mail válido, honeypot vazio e token com tempo decorrido deve passar."""
        data = {
            'username': 'leitorlegitimo',
            'email': 'leitor.legitimo@gmail.com',
            'password1': 'SenhaForte@2026',
            'password2': 'SenhaForte@2026',
            'website_hp': '',
            'bot_token': self.valid_human_token,
        }
        form = CustomSignupForm(data=data)
        self.assertTrue(form.is_valid(), f"Erros inesperados: {form.errors}")


class ContactViewAntiBotTestCase(TestCase):
    """Testa a proteção anti-bot no formulário de contato."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
        mail.outbox = []
        from django.core import signing
        from core.utils.anti_bot import SALT_BOT_TOKEN
        self.valid_human_token = signing.dumps({'ts': time.time() - 4.0}, salt=SALT_BOT_TOKEN)

    def test_contact_honeypot_discards_email(self):
        """Se o honeypot for preenchido, o e-mail não deve ser enviado."""
        data = {
            'name': 'Spam Bot',
            'email': 'spambot@example.com',
            'category': 'general',
            'subject': 'Ganhe um carro agora!',
            'message': 'Visite nosso site de prêmios.',
            'website_hp': 'http://spam.ru',
            'bot_token': self.valid_human_token,
        }
        request = self.factory.post('/contato/', data)
        # Configura mensagens na request
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ContactView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Redireciona com sucesso
        self.assertEqual(len(mail.outbox), 0)  # NENHUM e-mail enviado ao Brevo!

    def test_contact_fast_submission_discards_email(self):
        """Se submetido em menos de 2s, descarta silenciosamente."""
        data = {
            'name': 'Fast Bot',
            'email': 'fastbot@example.com',
            'category': 'general',
            'subject': 'Spam subject',
            'message': 'Fast spam message.',
            'website_hp': '',
            'bot_token': generate_bot_token(),  # Gerado agora (< 2s)
        }
        request = self.factory.post('/contato/', data)
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ContactView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)  # E-mail descartado!

    def test_contact_legitimate_sends_email(self):
        """Mensagem legítima de leitor humano deve enviar o e-mail com sucesso."""
        data = {
            'name': 'Maria Leitora',
            'email': 'maria.leitora@gmail.com',
            'category': 'general',
            'subject': 'Dúvida sobre envio de livro',
            'message': 'Gostaria de saber o prazo para o Rio de Janeiro.',
            'website_hp': '',
            'bot_token': self.valid_human_token,
        }
        request = self.factory.post('/contato/', data)
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ContactView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)  # E-mail enviado!
        self.assertIn('[CG.BookStore]', mail.outbox[0].subject)
        self.assertIn('Maria Leitora', mail.outbox[0].body)

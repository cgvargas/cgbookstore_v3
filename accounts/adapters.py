"""
Adapters customizados para django-allauth.

Estes adapters controlam o comportamento de autenticação e
integração com contas sociais (Google, Facebook).
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapter customizado para autenticação de contas.

    Permite customizar comportamento de registro, login, verificação de email, etc.

    Comportamento de verificação de email:
    - NOVOS usuários: devem verificar email antes de fazer login (mandatory)
    - Usuários JÁ VERIFICADOS: não bloqueiam no login
    - Previne pedidos repetidos de confirmação para usuários existentes
    """

    def is_open_for_signup(self, request):
        """
        Permite ou bloqueia novos registros.

        Útil para modo de manutenção ou registro por convite apenas.
        """
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def send_mail(self, template_prefix, email, context):
        """
        Sobrescreve envio de email para usar formato HTML.

        O allauth por padrão envia apenas texto simples. Este método
        garante que emails sejam enviados em HTML com fallback para texto.

        Args:
            template_prefix: Prefixo do template (ex: 'account/email/email_confirmation')
            email: Email do destinatário
            context: Contexto para renderizar o template
        """
        # Renderizar subject (sempre .txt)
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        # Remove quebras de linha do subject
        subject = ' '.join(subject.splitlines()).strip()
        # Adicionar prefixo se configurado
        subject_prefix = getattr(settings, 'ACCOUNT_EMAIL_SUBJECT_PREFIX', '')
        if subject_prefix:
            subject = subject_prefix + subject

        # Renderizar corpo do email
        # Tentar HTML primeiro, depois fallback para texto
        try:
            html_body = render_to_string(f'{template_prefix}_message.html', context)
            text_body = render_to_string(f'{template_prefix}_message.txt', context)

            # Criar email com HTML e alternativa texto
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,  # Corpo em texto simples (fallback)
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL'),
                to=[email]
            )
            msg.attach_alternative(html_body, "text/html")  # Versão HTML
            msg.send()

            logger.info(f"Email HTML enviado para {email}: {subject}")

        except Exception as e:
            # Fallback: enviar apenas texto simples
            logger.warning(f"Falha ao enviar HTML, usando texto simples: {e}")
            text_body = render_to_string(f'{template_prefix}_message.txt', context)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL'),
                to=[email]
            )
            msg.send()

            logger.info(f"Email texto enviado para {email}: {subject}")

    def login(self, request, user):
        """
        Sobrescreve método de login para permitir usuários já verificados
        entrarem sem pedir confirmação novamente.

        Verifica se usuário já tem email verificado antes de aplicar
        regra de ACCOUNT_EMAIL_VERIFICATION='mandatory'
        """
        from allauth.account.models import EmailAddress

        # Verificar se usuário tem pelo menos um email verificado
        has_verified_email = EmailAddress.objects.filter(
            user=user,
            verified=True
        ).exists()

        if has_verified_email:
            # Usuário já verificado - permitir login normalmente
            # Chama o método da superclasse do DefaultAccountAdapter (não o do allauth)
            return super().login(request, user)

        # Usuário não verificado - seguir comportamento padrão
        # (vai bloquear se ACCOUNT_EMAIL_VERIFICATION='mandatory')
        return super().login(request, user)

    def save_user(self, request, user, form, commit=True):
        """
        Salva usuário com dados extras do formulário.

        IMPORTANTE: EmailAddress é criado automaticamente pelo allauth
        via setup_user_email() após este método. Não criar aqui!
        """
        user = super().save_user(request, user, form, commit=False)

        # Adicionar lógica customizada aqui se necessário
        # Por exemplo: user.is_active = False (para aprovar manualmente)

        if commit:
            user.save()
            logger.info(f"Usuário salvo com sucesso: {user.username}")

        # NÃO criar EmailAddress aqui!
        # O allauth cria automaticamente em allauth.account.utils.setup_user_email()
        # que é chamado DEPOIS deste método. Se criarmos aqui, haverá AssertionError.

        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado para contas sociais (Google, Facebook).

    Responsável por:
    - Conectar contas sociais a usuários existentes
    - Popular UserProfile com dados do provider
    - Extrair informações relevantes (avatar, nome, etc.)
    """

    def pre_social_login(self, request, sociallogin):
        """
        Chamado ANTES do usuário fazer social login.

        Conecta conta social a User existente se email coincidir.
        Isso permite que usuários que já têm conta possam fazer
        login social sem criar conta duplicada.
        """
        # Se usuário já está logado, não fazer nada
        if request.user.is_authenticated:
            return

        # Se não tem email, não pode conectar
        if not sociallogin.email_addresses:
            return

        # Pegar email do social login
        email = sociallogin.email_addresses[0].email

        if not email:
            return

        # Buscar User existente com esse email
        try:
            user = User.objects.get(email=email)

            # Conectar social account ao user existente
            sociallogin.connect(request, user)

            logger.info(
                f"Conta social {sociallogin.account.provider} "
                f"conectada ao usuário existente: {user.username}"
            )

        except User.DoesNotExist:
            # User não existe, será criado no signup
            pass
        except User.MultipleObjectsReturned:
            # Múltiplos users com mesmo email (não deveria acontecer)
            logger.warning(
                f"Múltiplos usuários com email {email}. "
                f"Não conectando conta social automaticamente."
            )
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Popula User com dados do provider social.

        Extrai first_name, last_name, email do provider.
        """
        user = super().populate_user(request, sociallogin, data)

        # Extrair dados do provider
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Preencher campos do User baseado no provider
        if provider == 'google':
            # Google fornece: given_name, family_name, email, picture
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')

        elif provider == 'facebook':
            # Facebook fornece: first_name, last_name, email, picture
            user.first_name = extra_data.get('first_name', '')
            user.last_name = extra_data.get('last_name', '')

        # Se não tem nome, usar parte do email
        if not user.first_name and user.email:
            user.first_name = user.email.split('@')[0]

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Salva User após social login e popula UserProfile.

        Este é o melhor lugar para preencher o UserProfile com
        dados do provider (avatar, bio, localização, etc.)
        """
        user = super().save_user(request, sociallogin, form)

        # Garantir que UserProfile existe (signal já deve ter criado)
        try:
            profile = user.userprofile
        except Exception:
            # Se por algum motivo não existe, criar
            from accounts.models import UserProfile
            profile = UserProfile.objects.create(user=user)
            logger.info(f"UserProfile criado manualmente para {user.username}")

        # Extrair dados do provider
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Popular UserProfile baseado no provider
        updated_fields = []

        if provider == 'google':
            # Avatar do Google
            if 'picture' in extra_data and extra_data['picture']:
                profile.avatar = extra_data['picture']
                updated_fields.append('avatar')

            # Localização (locale)
            if 'locale' in extra_data and extra_data['locale']:
                # Converter locale do Google (ex: pt-BR) para nosso formato
                locale = extra_data['locale'].replace('-', '_').lower()
                profile.preferred_language = locale
                updated_fields.append('preferred_language')

        elif provider == 'facebook':
            # Avatar do Facebook
            if 'id' in extra_data:
                # URL da foto de perfil do Facebook
                fb_id = extra_data['id']
                profile.avatar = f"https://graph.facebook.com/{fb_id}/picture?type=large"
                updated_fields.append('avatar')

            # Localização (location)
            if 'location' in extra_data and extra_data['location']:
                location_name = extra_data['location'].get('name', '')
                if location_name:
                    profile.location = location_name
                    updated_fields.append('location')

            # Locale
            if 'locale' in extra_data and extra_data['locale']:
                locale = extra_data['locale'].replace('_', '-').lower()
                profile.preferred_language = locale
                updated_fields.append('preferred_language')

            # Link do perfil
            if 'link' in extra_data and extra_data['link']:
                profile.website = extra_data['link']
                updated_fields.append('website')

        # Salvar UserProfile se houve mudanças
        if updated_fields:
            profile.save()
            logger.info(
                f"UserProfile atualizado para {user.username} "
                f"com dados do {provider}. "
                f"Campos: {', '.join(updated_fields)}"
            )
        else:
            logger.info(
                f"UserProfile não foi atualizado para {user.username} "
                f"(nenhum dado relevante do {provider})"
            )

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        URL de redirecionamento após conectar uma conta social.

        Redireciona para página de gerenciar contas sociais.
        """
        return '/profile/edit/'  # Ou criar página específica

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Permite signup automático via social login.

        Se retornar False, usuário precisa preencher formulário
        adicional antes de criar conta.
        """
        # Sempre permitir signup automático
        return True

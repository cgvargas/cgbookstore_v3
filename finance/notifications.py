"""
Sistema de notificações por email para o módulo financeiro
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_payment_confirmation_email(subscription):
    """
    Envia email de confirmação de pagamento aprovado

    Args:
        subscription: Instância do modelo Subscription
    """
    try:
        user = subscription.user
        subject = "✅ Pagamento Aprovado - CGBookStore Premium"

        # Contexto para o template
        context = {
            'user': user,
            'subscription': subscription,
            'expiration_date': subscription.expiration_date,
            'price': subscription.price,
            'payment_method': subscription.get_payment_method_display(),
            'site_url': settings.SITE_URL,
        }

        # Renderiza template HTML
        html_content = render_to_string('finance/emails/payment_confirmation.html', context)

        # Versão texto puro (fallback)
        text_content = f"""
Olá {user.get_full_name() or user.username}!

Seu pagamento foi aprovado com sucesso! 🎉

Detalhes da Assinatura:
- Status: Ativa
- Valor: R$ {subscription.price}
- Método: {subscription.get_payment_method_display()}
- Válida até: {subscription.expiration_date.strftime('%d/%m/%Y %H:%M')}

Você agora tem acesso a todos os recursos Premium:
✓ Chatbot Literário Ilimitado
✓ Recomendações Personalizadas
✓ Análise Avançada de Preferências
✓ Sem Anúncios

Acesse sua conta: {settings.SITE_URL}/profile/

Obrigado por assinar o CGBookStore Premium!

Equipe CGBookStore
        """

        # Cria email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")

        # Envia
        email.send(fail_silently=False)
        logger.info(f"Email de confirmação enviado para {user.email}")

        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmação: {str(e)}")
        return False


def send_subscription_expiring_email(subscription, days_remaining):
    """
    Envia email avisando que a assinatura está expirando

    Args:
        subscription: Instância do modelo Subscription
        days_remaining: Dias restantes até expiração
    """
    try:
        user = subscription.user
        subject = f"⚠️ Sua assinatura Premium expira em {days_remaining} dias"

        context = {
            'user': user,
            'subscription': subscription,
            'days_remaining': days_remaining,
            'expiration_date': subscription.expiration_date,
            'renewal_url': f"{settings.SITE_URL}/finance/subscription/checkout/",
            'site_url': settings.SITE_URL,
        }

        html_content = render_to_string('finance/emails/subscription_expiring.html', context)

        text_content = f"""
Olá {user.get_full_name() or user.username}!

Sua assinatura Premium do CGBookStore expira em {days_remaining} dias.

Detalhes:
- Data de Expiração: {subscription.expiration_date.strftime('%d/%m/%Y %H:%M')}
- Status Atual: {subscription.get_status_display()}

Para continuar aproveitando todos os recursos Premium, renove sua assinatura:
{settings.SITE_URL}/finance/subscription/checkout/

Recursos Premium:
✓ Chatbot Literário Ilimitado
✓ Recomendações Personalizadas
✓ Análise Avançada
✓ Sem Anúncios

Não perca o acesso aos seus recursos favoritos!

Equipe CGBookStore
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Email de expiração enviado para {user.email} ({days_remaining} dias)")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email de expiração: {str(e)}")
        return False


def send_subscription_expired_email(subscription):
    """
    Envia email informando que a assinatura expirou

    Args:
        subscription: Instância do modelo Subscription
    """
    try:
        user = subscription.user
        subject = "❌ Sua assinatura Premium expirou - CGBookStore"

        context = {
            'user': user,
            'subscription': subscription,
            'renewal_url': f"{settings.SITE_URL}/finance/subscription/checkout/",
            'site_url': settings.SITE_URL,
        }

        html_content = render_to_string('finance/emails/subscription_expired.html', context)

        text_content = f"""
Olá {user.get_full_name() or user.username}!

Sua assinatura Premium do CGBookStore expirou.

Você ainda pode continuar usando o CGBookStore com acesso gratuito, mas alguns recursos Premium não estarão mais disponíveis:
- Chatbot Literário (limite de uso)
- Recomendações Personalizadas Avançadas
- Análises Detalhadas

Quer reativar sua assinatura?
Renove agora por apenas R$ 9,90/mês:
{settings.SITE_URL}/finance/subscription/checkout/

Sentiremos sua falta! 💔

Equipe CGBookStore
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Email de expiração confirmada enviado para {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email de expiração: {str(e)}")
        return False


def send_payment_failed_email(subscription, reason=''):
    """
    Envia email informando que o pagamento falhou

    Args:
        subscription: Instância do modelo Subscription
        reason: Motivo da falha
    """
    try:
        user = subscription.user
        subject = "⚠️ Problema com seu pagamento - CGBookStore Premium"

        context = {
            'user': user,
            'subscription': subscription,
            'reason': reason,
            'retry_url': f"{settings.SITE_URL}/finance/subscription/checkout/",
            'site_url': settings.SITE_URL,
        }

        html_content = render_to_string('finance/emails/payment_failed.html', context)

        text_content = f"""
Olá {user.get_full_name() or user.username}!

Identificamos um problema com seu pagamento para a assinatura Premium.

Motivo: {reason or 'Não especificado'}

O que fazer:
1. Verifique os dados do seu pagamento
2. Tente novamente com outro método de pagamento
3. Entre em contato com nosso suporte se o problema persistir

Tentar novamente:
{settings.SITE_URL}/finance/subscription/checkout/

Estamos aqui para ajudar!

Equipe CGBookStore
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Email de falha de pagamento enviado para {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email de falha: {str(e)}")
        return False

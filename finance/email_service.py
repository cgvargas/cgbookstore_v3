"""
Serviço de E-mail para Premium
CGBookStore v3

Responsável por enviar e-mails relacionados a assinaturas Premium:
- Boas-vindas ao Premium
- Confirmação de pagamento
- Lembrete de expiração
"""

import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class PremiumEmailService:
    """
    Serviço para envio de e-mails relacionados ao Premium.
    
    Usa templates HTML com fallback para texto simples.
    """
    
    @staticmethod
    def send_welcome_email(user, subscription=None, expires_at=None, price="9,90",
                           badge_context=None, is_free_campaign=False):
        """
        Envia e-mail de boas-vindas ao Premium.
        
        Args:
            user: Instância do modelo User
            subscription: Instância do modelo Subscription (opcional)
            expires_at: Data de expiração (datetime ou None)
            price: Valor pago (string formatada)
            badge_context: Dict com dados do badge Premium (opcional)
            is_free_campaign: True se a assinatura é via campanha gratuita
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        import os
        from email.mime.image import MIMEImage

        try:
            # Preparar contexto base
            context = {
                'username': user.get_full_name() or user.username,
                'email': user.email,
                'price': price,
                'expires_at': expires_at.strftime('%d/%m/%Y') if expires_at else 'N/A',
                'site_url': settings.SITE_URL,
                'current_year': timezone.now().year,
                'is_free_campaign': is_free_campaign,
                # A imagem é embutida via CID (não precisa de URL externa)
                'badge_image_src': 'cid:premium_badge',
            }

            # Adicionar contexto do badge Premium ao e-mail
            if badge_context:
                context.update(badge_context)
            else:
                from finance.badge_service import get_premium_badge_context
                context.update(get_premium_badge_context())

            # Sempre usar CID como src da imagem no template
            context['badge_image_src'] = 'cid:premium_badge'

            # Renderizar templates
            html_body = render_to_string('emails/premium_welcome.html', context)
            text_body = render_to_string('emails/premium_welcome.txt', context)

            # Criar e enviar e-mail
            subject = '[CGBookStore] 🎉 Bem-vindo ao Premium!'

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.mixed_subtype = 'related'
            msg.attach_alternative(html_body, "text/html")

            # Embutir imagem do badge como anexo inline (CID)
            badge_image_path = os.path.join(
                settings.BASE_DIR, 'static', 'images', 'badges', 'premium_badge.png'
            )
            if os.path.exists(badge_image_path):
                with open(badge_image_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                inline_image = MIMEImage(img_data)
                inline_image.add_header('Content-ID', '<premium_badge>')
                inline_image.add_header('Content-Disposition', 'inline', filename='premium_badge.png')
                msg.attach(inline_image)
                logger.debug("Imagem do badge embutida no e-mail via CID usando MIMEImage.")
            else:
                logger.warning(f"Imagem do badge não encontrada em: {badge_image_path}")

            msg.send()

            logger.info(f"E-mail de boas-vindas Premium enviado para {user.email}")
            return True

        except Exception as e:
            logger.exception(f"Erro ao enviar e-mail de boas-vindas Premium para {user.email}: {e}")
            return False

    
    @staticmethod
    def send_expiring_reminder(user, days_left, expires_at):
        """
        Envia lembrete de Premium expirando.
        
        Args:
            user: Instância do modelo User
            days_left: Dias restantes (int)
            expires_at: Data de expiração (datetime)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Determinar urgência e subject (sem emojis para evitar problemas de encoding)
            if days_left <= 1:
                subject = '[CGBookStore] Seu Premium expira amanha - Renove agora'
            elif days_left <= 3:
                subject = f'[CGBookStore] Seu Premium expira em {days_left} dias'
            else:
                subject = f'[CGBookStore] Lembrete: Seu Premium expira em {days_left} dias'
            
            # Garantir nome do usuário sem problemas de encoding
            username = user.get_full_name() or user.username
            # Normalizar caracteres acentuados
            if username:
                username = username.encode('utf-8').decode('utf-8')
            
            context = {
                'username': username,
                'days_left': days_left,
                'expires_at': expires_at.strftime('%d/%m/%Y às %H:%M'),
                'site_url': settings.SITE_URL,
                'current_year': timezone.now().year,
                'price': '9,90',  # Valor do plano
            }
            
            # Renderizar templates com encoding UTF-8
            html_body = render_to_string('emails/premium_expiring.html', context)
            text_body = render_to_string('emails/premium_expiring.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            # Garantir charset UTF-8
            msg.encoding = 'utf-8'
            msg.attach_alternative(html_body, "text/html; charset=utf-8")
            msg.send()
            
            logger.info(f"E-mail de lembrete Premium enviado para {user.email} ({days_left} dias)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete Premium para {user.email}: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation(user, payment_id, amount, payment_method='pix'):
        """
        Envia confirmação de pagamento.
        
        Args:
            user: Instância do modelo User
            payment_id: ID do pagamento
            amount: Valor pago (Decimal ou float)
            payment_method: Método de pagamento
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            subject = '[CGBookStore] ✅ Pagamento confirmado!'
            
            context = {
                'username': user.get_full_name() or user.username,
                'payment_id': payment_id,
                'amount': f"{float(amount):.2f}".replace('.', ','),
                'payment_method': payment_method.upper(),
                'site_url': settings.SITE_URL,
                'current_year': timezone.now().year,
            }
            
            # TODO: Criar template payment_confirmation.html
            # Por enquanto, usar e-mail simples
            text_body = f"""
Olá {context['username']},

Seu pagamento foi confirmado com sucesso!

📋 Detalhes:
• ID do Pagamento: {context['payment_id']}
• Valor: R$ {context['amount']}
• Método: {context['payment_method']}

Seu Premium já está ativo! Acesse:
{settings.SITE_URL}/dashboard/

Equipe CGBookStore
"""
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.send()
            
            logger.info(f"E-mail de confirmação de pagamento enviado para {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar confirmação de pagamento para {user.email}: {e}")
            return False

    @staticmethod
    def send_winback_email(user, expired_at):
        """
        Envia email de win-back para usuários que deixaram o Premium expirar.
        
        Args:
            user: Instância do modelo User
            expired_at: Data em que o Premium expirou (datetime)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            subject = '[CGBookStore] 💔 Sentimos sua falta... Volte a ser Premium!'
            
            context = {
                'username': user.get_full_name() or user.username,
                'expired_at': expired_at.strftime('%d/%m/%Y'),
                'site_url': settings.SITE_URL,
                'current_year': timezone.now().year,
            }
            
            # Renderizar templates
            html_body = render_to_string('emails/premium_expired.html', context)
            text_body = render_to_string('emails/premium_expired.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            
            logger.info(f"E-mail de win-back enviado para {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de win-back para {user.email}: {e}")
            return False


# Função helper para uso rápido
def send_premium_welcome(user, expires_at=None, price="9,90"):
    """Atalho para enviar e-mail de boas-vindas Premium."""
    return PremiumEmailService.send_welcome_email(user, expires_at=expires_at, price=price)

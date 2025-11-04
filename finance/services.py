import mercadopago
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import logging
from .models import Subscription, Order, TransactionLog, Campaign, CampaignGrant

logger = logging.getLogger(__name__)

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    def create_subscription_preference(self, user, payment_method='pix'):
        try:
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={'payment_method': payment_method, 'price': Decimal('9.90'), 'status': 'pendente'}
            )
            preference_data = {
                "items": [{
                    "title": "CGBookStore Premium - Assinatura Mensal",
                    "description": "Acesso premium ao chatbot literario",
                    "quantity": 1,
                    "unit_price": float(subscription.price),
                    "currency_id": "BRL"
                }],
                "payer": {
                    "name": user.get_full_name() or user.username,
                    "email": user.email
                },
                "external_reference": f"subscription_{subscription.id}",
                "statement_descriptor": "CGBookStore Premium"
            }

            # Adiciona URLs de retorno apenas se nao for localhost
            if not settings.SITE_URL.startswith('http://localhost') and not settings.SITE_URL.startswith('http://127.0.0.1'):
                preference_data["back_urls"] = {
                    "success": f"{settings.SITE_URL}/finance/subscription/success/",
                    "failure": f"{settings.SITE_URL}/finance/subscription/failure/",
                    "pending": f"{settings.SITE_URL}/finance/subscription/pending/"
                }
                preference_data["auto_return"] = "approved"
                preference_data["notification_url"] = f"{settings.SITE_URL}/finance/webhook/mercadopago/"
            preference_response = self.sdk.preference().create(preference_data)

            # Verifica se a resposta foi bem sucedida
            if preference_response["status"] != 201:
                error_msg = preference_response.get("response", {}).get("message", "Erro desconhecido ao criar preferencia")
                logger.error(f"Erro na API do Mercado Pago: {error_msg} - Status: {preference_response['status']}")
                return {"success": False, "error": f"Erro na comunicacao com Mercado Pago: {error_msg}"}

            preference = preference_response["response"]

            # Verifica se o ID foi retornado
            if "id" not in preference:
                logger.error(f"Resposta invalida do Mercado Pago: {preference_response}")
                return {"success": False, "error": "Credenciais do Mercado Pago invalidas ou nao configuradas. Verifique o arquivo .env"}

            # Usa sandbox_init_point se disponivel (para credenciais de teste), senao usa init_point
            init_point = preference.get("sandbox_init_point") or preference.get("init_point")

            if not init_point:
                logger.error(f"Nenhum init_point encontrado na resposta: {preference_response}")
                return {"success": False, "error": "Erro ao obter URL de checkout do Mercado Pago"}

            subscription.mp_preference_id = preference["id"]
            subscription.save()

            logger.info(f"Preferencia criada com sucesso: {preference['id']}")
            return {"success": True, "preference_id": preference["id"], "init_point": init_point, "subscription_id": subscription.id}
        except KeyError as e:
            logger.error(f"Erro ao acessar chave na resposta: {str(e)} - Response: {preference_response if 'preference_response' in locals() else 'N/A'}")
            return {"success": False, "error": "Credenciais do Mercado Pago invalidas. Verifique se o ACCESS_TOKEN esta configurado corretamente no .env"}
        except Exception as e:
            logger.error(f"Erro ao criar preferencia: {str(e)}")
            return {"success": False, "error": f"Erro inesperado: {str(e)}"}
    
    def process_webhook(self, data):
        try:
            topic = data.get("topic") or data.get("type")
            return {"success": True, "message": f"Topico {topic} recebido"}
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {"success": False, "error": str(e)}


class CampaignService:
    """
    Serviço para gerenciar campanhas de marketing e concessão de Premium gratuito
    """

    @staticmethod
    def get_eligible_users(campaign):
        """
        Retorna QuerySet de usuários elegíveis baseado nos critérios da campanha

        Args:
            campaign: Instância do modelo Campaign

        Returns:
            QuerySet de User
        """
        criteria = campaign.criteria
        target_type = campaign.target_type
        users = User.objects.all()

        # Exclui usuários que já receberam desta campanha
        already_granted_ids = CampaignGrant.objects.filter(
            campaign=campaign
        ).values_list('user_id', flat=True)
        users = users.exclude(id__in=already_granted_ids)

        if target_type == 'individual':
            # Usuário individual por ID, username ou email
            user_id = criteria.get('user_id')
            username = criteria.get('username')
            email = criteria.get('email')

            if user_id:
                users = users.filter(id=user_id)
            elif username:
                users = users.filter(username=username)
            elif email:
                users = users.filter(email=email)

        elif target_type == 'group':
            # Grupo de usuários por lista de IDs ou usernames
            user_ids = criteria.get('user_ids', [])
            usernames = criteria.get('usernames', [])
            limit = criteria.get('limit')  # Limite de quantidade

            if user_ids:
                users = users.filter(id__in=user_ids)
            elif usernames:
                users = users.filter(username__in=usernames)

            if limit:
                users = users[:limit]

        elif target_type == 'new_users':
            # Novos usuários cadastrados após uma data
            registered_after = criteria.get('registered_after')
            days_ago = criteria.get('days_ago', 7)  # Padrão: últimos 7 dias

            if registered_after:
                users = users.filter(date_joined__gte=registered_after)
            else:
                cutoff_date = timezone.now() - timedelta(days=days_ago)
                users = users.filter(date_joined__gte=cutoff_date)

        elif target_type == 'birthdays':
            # Aniversariantes do mês atual
            current_month = timezone.now().month
            # Nota: Isso assume que existe um campo 'birthday' no modelo User ou UserProfile
            # Se não existir, precisamos usar date_joined como alternativa
            try:
                # Tenta filtrar por campo birthday no UserProfile
                users = users.filter(userprofile__birthday__month=current_month)
            except:
                # Fallback: usa mês de cadastro
                users = users.filter(date_joined__month=current_month)

        elif target_type == 'custom':
            # Critérios personalizados
            # Usuários sem assinatura ativa
            if criteria.get('no_active_subscription'):
                active_subscription_ids = Subscription.objects.filter(
                    status='ativa'
                ).values_list('user_id', flat=True)
                users = users.exclude(id__in=active_subscription_ids)

            # Usuários inativos há X dias
            inactive_days = criteria.get('inactive_days')
            if inactive_days:
                cutoff_date = timezone.now() - timedelta(days=inactive_days)
                users = users.filter(last_login__lt=cutoff_date)

            # Usuários com assinatura expirada
            if criteria.get('expired_subscription'):
                expired_ids = Subscription.objects.filter(
                    status='expirada'
                ).values_list('user_id', flat=True)
                users = users.filter(id__in=expired_ids)

        # Aplicar distinct() ANTES do slice
        users = users.distinct()

        # Limite de quantidade (aplicar DEPOIS do distinct)
        if target_type == 'custom':
            limit = criteria.get('limit')
            if limit:
                users = users[:limit]

        return users

    @staticmethod
    def grant_premium(user, campaign, reason=''):
        """
        Concede Premium gratuito para um usuário

        Args:
            user: Instância do modelo User
            campaign: Instância do modelo Campaign
            reason: Motivo/observação opcional

        Returns:
            dict com success e dados da concessão
        """
        try:
            # Verifica se a campanha ainda pode conceder
            if not campaign.can_grant_more():
                return {
                    'success': False,
                    'error': 'Campanha atingiu o limite de concessões'
                }

            # Verifica se o usuário já recebeu desta campanha
            if CampaignGrant.objects.filter(campaign=campaign, user=user).exists():
                return {
                    'success': False,
                    'error': 'Usuário já recebeu Premium desta campanha'
                }

            # Criar ou obter assinatura
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={
                    'payment_method': 'pix',  # Método padrão para campanhas
                    'price': Decimal('0.00'),  # Gratuito
                    'status': 'pendente'
                }
            )

            # Ativar assinatura com duração da campanha
            subscription.activate(
                duration_days=campaign.duration_days,
                is_free_campaign=True
            )

            # Calcular data de expiração
            expires_at = timezone.now() + timedelta(days=campaign.duration_days)

            # Criar registro de concessão
            grant = CampaignGrant.objects.create(
                campaign=campaign,
                user=user,
                subscription=subscription,
                expires_at=expires_at,
                reason=reason,
                is_active=True,
                was_notified=False
            )

            # Atualizar UserProfile (se existir)
            try:
                profile = user.userprofile
                profile.is_premium = True
                profile.premium_expires_at = expires_at
                profile.save()
            except:
                logger.warning(f"UserProfile não encontrado para {user.username}")

            # Atualizar estatísticas da campanha
            campaign.total_granted += 1
            campaign.save()

            # Enviar notificação se habilitado
            if campaign.send_notification:
                try:
                    from accounts.models import CampaignNotification
                    notification = CampaignNotification.create_premium_granted_notification(
                        user=user,
                        campaign=campaign,
                        grant=grant
                    )
                    logger.info(f"Notificação enviada para {user.username}: {notification.id}")
                except Exception as e:
                    logger.warning(f"Erro ao enviar notificação para {user.username}: {str(e)}")

            logger.info(f"Premium concedido: {user.username} via campanha {campaign.name}")

            return {
                'success': True,
                'grant_id': grant.id,
                'user': user.username,
                'expires_at': expires_at
            }

        except Exception as e:
            logger.error(f"Erro ao conceder Premium: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def revoke_premium(grant):
        """
        Revoga Premium concedido por campanha

        Args:
            grant: Instância do modelo CampaignGrant

        Returns:
            dict com success
        """
        try:
            # Revoga a concessão
            grant.revoke()

            # Atualizar UserProfile
            try:
                profile = grant.user.userprofile
                profile.is_premium = False
                profile.premium_expires_at = None
                profile.save()
            except:
                logger.warning(f"UserProfile não encontrado para {grant.user.username}")

            logger.info(f"Premium revogado: {grant.user.username} da campanha {grant.campaign.name}")

            return {'success': True}

        except Exception as e:
            logger.error(f"Erro ao revogar Premium: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def execute_campaign(campaign, preview=False):
        """
        Executa uma campanha completa, concedendo Premium aos elegíveis

        Args:
            campaign: Instância do modelo Campaign
            preview: Se True, apenas conta elegíveis sem conceder

        Returns:
            dict com estatísticas da execução
        """
        try:
            eligible_users = CampaignService.get_eligible_users(campaign)
            eligible_count = eligible_users.count()

            # Atualiza total de elegíveis
            campaign.total_eligible = eligible_count
            campaign.save()

            if preview:
                return {
                    'success': True,
                    'preview': True,
                    'eligible_count': eligible_count,
                    'eligible_users': list(eligible_users.values('id', 'username', 'email'))
                }

            # Executa concessão
            granted_count = 0
            errors = []

            for user in eligible_users:
                # Verifica se ainda pode conceder
                if not campaign.can_grant_more():
                    break

                result = CampaignService.grant_premium(user, campaign)
                if result['success']:
                    granted_count += 1
                else:
                    errors.append(f"{user.username}: {result.get('error')}")

            # Atualiza controle de execuções
            from django.db.models import F
            campaign.last_execution_date = timezone.now()
            campaign.execution_count = F('execution_count') + 1
            campaign.save(update_fields=['last_execution_date', 'execution_count'])

            # Recarrega para obter o valor atualizado do execution_count
            campaign.refresh_from_db()

            return {
                'success': True,
                'preview': False,
                'eligible_count': eligible_count,
                'granted_count': granted_count,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Erro ao executar campanha: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def check_expired_grants():
        """
        Verifica e revoga concessões expiradas

        Returns:
            dict com estatísticas da revogação
        """
        try:
            now = timezone.now()
            expired_grants = CampaignGrant.objects.filter(
                is_active=True,
                expires_at__lt=now
            )

            revoked_count = 0
            for grant in expired_grants:
                result = CampaignService.revoke_premium(grant)
                if result['success']:
                    revoked_count += 1

            logger.info(f"Concessões expiradas revogadas: {revoked_count}")

            return {
                'success': True,
                'revoked_count': revoked_count
            }

        except Exception as e:
            logger.error(f"Erro ao verificar concessões expiradas: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_campaign_stats(campaign):
        """
        Retorna estatísticas detalhadas de uma campanha

        Args:
            campaign: Instância do modelo Campaign

        Returns:
            dict com estatísticas
        """
        grants = CampaignGrant.objects.filter(campaign=campaign)

        return {
            'total_granted': grants.count(),
            'active_grants': grants.filter(is_active=True).count(),
            'expired_grants': grants.filter(is_active=False).count(),
            'pending_notifications': grants.filter(was_notified=False).count(),
            'eligible_count': campaign.total_eligible,
            'remaining_grants': campaign.get_remaining_grants()
        }

"""
Serviço de pagamentos para Plataforma de Talentos
Estende o MercadoPagoService existente do app finance
"""
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from finance.services import MercadoPagoService
from ..models import (
    AuthorPlan,
    PublisherPlan,
    AuthorSubscription,
    PublisherSubscription
)

logger = logging.getLogger(__name__)


class TalentPlatformPaymentService(MercadoPagoService):
    """
    Serviço de pagamentos para Autores e Editoras
    Herda de MercadoPagoService para reaproveitar código existente
    """

    def create_author_subscription_preference(self, author, plan, billing_cycle='monthly'):
        """
        Cria preferência de pagamento para assinatura de autor

        Args:
            author: EmergingAuthor instance
            plan: AuthorPlan instance
            billing_cycle: 'monthly' ou 'yearly'

        Returns:
            dict com 'success', 'init_point', etc.
        """
        try:
            # Determinar preço baseado no ciclo
            if billing_cycle == 'yearly':
                price = float(plan.price_yearly)
                description = f"Assinatura Anual - {plan.name}"
                period_months = 12
            else:
                price = float(plan.price_monthly)
                description = f"Assinatura Mensal - {plan.name}"
                period_months = 1

            # Criar ou atualizar assinatura
            subscription, created = AuthorSubscription.objects.get_or_create(
                author=author,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'status': 'pendente'
                }
            )

            if not created:
                subscription.plan = plan
                subscription.billing_cycle = billing_cycle
                subscription.status = 'pendente'
                subscription.save()

            # Criar preferência no MercadoPago
            preference_data = {
                "items": [{
                    "title": description,
                    "description": f"Plano {plan.name} para Autores Emergentes - CG.BookStore",
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "BRL"
                }],
                "payer": {
                    "name": author.user.get_full_name() or author.user.username,
                    "email": author.user.email
                },
                "external_reference": f"author_sub_{subscription.id}_plan_{plan.id}",
                "statement_descriptor": "CGBOOKSTORE AUTOR"
            }

            # Adicionar URLs de retorno se não for localhost
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            if not site_url.startswith('http://localhost') and not site_url.startswith('http://127.0.0.1'):
                preference_data["back_urls"] = {
                    "success": f"{site_url}/novos-autores/pagamento/sucesso/",
                    "failure": f"{site_url}/novos-autores/pagamento/falha/",
                    "pending": f"{site_url}/novos-autores/pagamento/pendente/"
                }
                preference_data["auto_return"] = "approved"
                preference_data["notification_url"] = f"{site_url}/novos-autores/webhook/mercadopago/"

            # Criar preferência
            preference_response = self.sdk.preference().create(preference_data)

            # Verificar resposta
            if preference_response["status"] != 201:
                error_msg = preference_response.get("response", {}).get("message", "Erro desconhecido")
                logger.error(f"Erro na API do MercadoPago: {error_msg}")
                return {"success": False, "error": f"Erro ao criar preferência: {error_msg}"}

            preference = preference_response["response"]

            if "id" not in preference:
                logger.error(f"Resposta inválida do MercadoPago: {preference_response}")
                return {"success": False, "error": "Credenciais do MercadoPago inválidas"}

            # Obter init_point (sandbox ou produção)
            init_point = preference.get("sandbox_init_point") or preference.get("init_point")

            if not init_point:
                return {"success": False, "error": "Erro ao obter URL de checkout"}

            # Salvar ID da preferência
            subscription.mercadopago_preference_id = preference["id"]
            subscription.save()

            logger.info(f"Preferência criada para autor {author.id}: {preference['id']}")

            return {
                "success": True,
                "preference_id": preference["id"],
                "init_point": init_point,
                "subscription_id": subscription.id
            }

        except Exception as e:
            logger.error(f"Erro ao criar preferência de autor: {str(e)}")
            return {"success": False, "error": f"Erro inesperado: {str(e)}"}

    def create_publisher_subscription_preference(self, publisher, plan, billing_cycle='monthly', is_trial=False):
        """
        Cria preferência de pagamento para assinatura de editora

        Args:
            publisher: PublisherProfile instance
            plan: PublisherPlan instance
            billing_cycle: 'monthly' ou 'yearly'
            is_trial: se é trial de 14 dias

        Returns:
            dict com 'success', 'init_point', etc.
        """
        try:
            # Determinar preço baseado no ciclo
            if billing_cycle == 'yearly':
                price = float(plan.price_yearly)
                description = f"Assinatura Anual - {plan.name}"
                period_months = 12
            else:
                price = float(plan.price_monthly)
                description = f"Assinatura Mensal - {plan.name}"
                period_months = 1

            # Se for trial, cobrar valor simbólico para validação de cartão
            if is_trial:
                price = 0.01
                description = f"Trial 14 Dias - {plan.name}"

            # Criar ou atualizar assinatura
            subscription, created = PublisherSubscription.objects.get_or_create(
                publisher=publisher,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'status': 'pendente'
                }
            )

            if not created:
                subscription.plan = plan
                subscription.billing_cycle = billing_cycle
                subscription.status = 'pendente'
                subscription.save()

            # Criar preferência no MercadoPago
            preference_data = {
                "items": [{
                    "title": description,
                    "description": f"Plano {plan.name} para Editoras - CG.BookStore",
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "BRL"
                }],
                "payer": {
                    "name": publisher.company_name,
                    "email": publisher.user.email
                },
                "external_reference": f"publisher_sub_{subscription.id}_plan_{plan.id}_trial_{is_trial}",
                "statement_descriptor": "CGBOOKSTORE EDITORA"
            }

            # Adicionar URLs de retorno se não for localhost
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            if not site_url.startswith('http://localhost') and not site_url.startswith('http://127.0.0.1'):
                preference_data["back_urls"] = {
                    "success": f"{site_url}/novos-autores/pagamento/sucesso/",
                    "failure": f"{site_url}/novos-autores/pagamento/falha/",
                    "pending": f"{site_url}/novos-autores/pagamento/pendente/"
                }
                preference_data["auto_return"] = "approved"
                preference_data["notification_url"] = f"{site_url}/novos-autores/webhook/mercadopago/"

            # Criar preferência
            preference_response = self.sdk.preference().create(preference_data)

            # Verificar resposta
            if preference_response["status"] != 201:
                error_msg = preference_response.get("response", {}).get("message", "Erro desconhecido")
                logger.error(f"Erro na API do MercadoPago: {error_msg}")
                return {"success": False, "error": f"Erro ao criar preferência: {error_msg}"}

            preference = preference_response["response"]

            if "id" not in preference:
                logger.error(f"Resposta inválida do MercadoPago: {preference_response}")
                return {"success": False, "error": "Credenciais do MercadoPago inválidas"}

            # Obter init_point (sandbox ou produção)
            init_point = preference.get("sandbox_init_point") or preference.get("init_point")

            if not init_point:
                return {"success": False, "error": "Erro ao obter URL de checkout"}

            # Salvar ID da preferência
            subscription.mercadopago_preference_id = preference["id"]
            subscription.save()

            logger.info(f"Preferência criada para editora {publisher.id}: {preference['id']}")

            return {
                "success": True,
                "preference_id": preference["id"],
                "init_point": init_point,
                "subscription_id": subscription.id,
                "is_trial": is_trial
            }

        except Exception as e:
            logger.error(f"Erro ao criar preferência de editora: {str(e)}")
            return {"success": False, "error": f"Erro inesperado: {str(e)}"}

    def process_author_payment(self, subscription_id, payment_status):
        """
        Processa pagamento de autor baseado no status

        Args:
            subscription_id: ID da AuthorSubscription
            payment_status: 'approved', 'pending', 'rejected', etc.

        Returns:
            bool indicando sucesso
        """
        try:
            subscription = AuthorSubscription.objects.get(id=subscription_id)

            if payment_status == 'approved':
                subscription.activate()
                logger.info(f"Assinatura de autor {subscription.id} ativada")
                return True
            elif payment_status in ['rejected', 'cancelled']:
                subscription.cancel()
                logger.info(f"Assinatura de autor {subscription.id} cancelada")
                return True
            else:
                subscription.status = 'pendente'
                subscription.save()
                return True

        except AuthorSubscription.DoesNotExist:
            logger.error(f"Assinatura {subscription_id} não encontrada")
            return False
        except Exception as e:
            logger.error(f"Erro ao processar pagamento de autor: {str(e)}")
            return False

    def process_publisher_payment(self, subscription_id, payment_status, is_trial=False):
        """
        Processa pagamento de editora baseado no status

        Args:
            subscription_id: ID da PublisherSubscription
            payment_status: 'approved', 'pending', 'rejected', etc.
            is_trial: se é trial de 14 dias

        Returns:
            bool indicando sucesso
        """
        try:
            subscription = PublisherSubscription.objects.get(id=subscription_id)

            if payment_status == 'approved':
                subscription.activate(is_trial=is_trial)
                logger.info(f"Assinatura de editora {subscription.id} ativada (trial={is_trial})")
                return True
            elif payment_status in ['rejected', 'cancelled']:
                subscription.cancel()
                logger.info(f"Assinatura de editora {subscription.id} cancelada")
                return True
            else:
                subscription.status = 'pendente'
                subscription.save()
                return True

        except PublisherSubscription.DoesNotExist:
            logger.error(f"Assinatura {subscription_id} não encontrada")
            return False
        except Exception as e:
            logger.error(f"Erro ao processar pagamento de editora: {str(e)}")
            return False

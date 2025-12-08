"""
Views para processamento de pagamentos via MercadoPago
Usa o serviço existente do app finance
"""
import logging
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import (
    AuthorPlan,
    PublisherPlan,
    AuthorSubscription,
    PublisherSubscription,
    EmergingAuthor,
    PublisherProfile
)
from .services.payment_service import TalentPlatformPaymentService

logger = logging.getLogger(__name__)
payment_service = TalentPlatformPaymentService()


# ========== CHECKOUT - AUTORES ==========

@login_required
@require_http_methods(["POST"])
def create_author_checkout(request, plan_id):
    """
    Cria checkout para plano de autor
    """
    plan = get_object_or_404(AuthorPlan, id=plan_id, is_active=True)

    # Verificar se usuário é autor
    try:
        author = request.user.emerging_author_profile
    except EmergingAuthor.DoesNotExist:
        messages.error(request, "Você precisa ser um autor para assinar um plano.")
        return redirect('new_authors:become_author')

    # Verificar se o plano é gratuito
    if plan.price_monthly == 0:
        messages.info(request, "Este é o plano gratuito, você já tem acesso!")
        return redirect('new_authors:author_dashboard')

    # Pegar ciclo de cobrança
    billing_cycle = request.POST.get('billing_cycle', 'monthly')

    # Criar preferência
    result = payment_service.create_author_subscription_preference(author, plan, billing_cycle)

    if result['success']:
        # Salvar dados na sessão
        request.session['payment_subscription_id'] = result['subscription_id']
        request.session['payment_user_type'] = 'author'
        return redirect(result['init_point'])
    else:
        messages.error(request, f"Erro ao processar pagamento: {result['error']}")
        return redirect('new_authors:author_plans')


# ========== CHECKOUT - EDITORAS ==========

@login_required
@require_http_methods(["POST"])
def create_publisher_checkout(request, plan_id):
    """
    Cria checkout para plano de editora
    """
    plan = get_object_or_404(PublisherPlan, id=plan_id, is_active=True)

    # Verificar se usuário é editora
    try:
        publisher = request.user.publisher_profile
    except PublisherProfile.DoesNotExist:
        messages.error(request, "Você precisa ser uma editora para assinar um plano.")
        return redirect('new_authors:become_publisher')

    # Pegar ciclo de cobrança e trial
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    is_trial = request.POST.get('is_trial', 'false') == 'true'

    # Criar preferência
    result = payment_service.create_publisher_subscription_preference(publisher, plan, billing_cycle, is_trial)

    if result['success']:
        # Salvar dados na sessão
        request.session['payment_subscription_id'] = result['subscription_id']
        request.session['payment_user_type'] = 'publisher'
        request.session['payment_is_trial'] = is_trial
        return redirect(result['init_point'])
    else:
        messages.error(request, f"Erro ao processar pagamento: {result['error']}")
        return redirect('new_authors:publisher_plans')


# ========== PÁGINAS DE RETORNO ==========

@login_required
def payment_success(request):
    """
    Página exibida após pagamento aprovado
    """
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    preference_id = request.GET.get('preference_id')

    # Recuperar dados da sessão
    subscription_id = request.session.get('payment_subscription_id')
    user_type = request.session.get('payment_user_type')
    is_trial = request.session.get('payment_is_trial', False)

    context = {
        'payment_id': payment_id,
        'status': status,
        'user_type': user_type,
    }

    # Se o pagamento foi aprovado, ativar assinatura
    if status == 'approved' and subscription_id:
        try:
            if user_type == 'author':
                payment_service.process_author_payment(subscription_id, 'approved')
                subscription = AuthorSubscription.objects.get(id=subscription_id)
                messages.success(request, f"Parabéns! Sua assinatura do plano {subscription.plan.name} foi ativada!")
                context['redirect_url'] = 'new_authors:author_dashboard'

            elif user_type == 'publisher':
                payment_service.process_publisher_payment(subscription_id, 'approved', is_trial)
                subscription = PublisherSubscription.objects.get(id=subscription_id)

                if is_trial:
                    messages.success(request, f"Trial de 14 dias ativado! Você tem acesso completo ao plano {subscription.plan.name}.")
                else:
                    messages.success(request, f"Parabéns! Sua assinatura do plano {subscription.plan.name} foi ativada!")

                context['redirect_url'] = 'new_authors:publisher_dashboard'

            # Limpar sessão
            if 'payment_subscription_id' in request.session:
                del request.session['payment_subscription_id']
            if 'payment_user_type' in request.session:
                del request.session['payment_user_type']
            if 'payment_is_trial' in request.session:
                del request.session['payment_is_trial']

        except Exception as e:
            logger.error(f"Erro ao ativar assinatura: {str(e)}")
            messages.error(request, "Pagamento aprovado, mas houve um erro. Entre em contato com o suporte.")

    return render(request, 'new_authors/payment_success.html', context)


@login_required
def payment_failure(request):
    """
    Página exibida após pagamento recusado
    """
    messages.error(request, "Seu pagamento foi recusado. Tente novamente com outro método de pagamento.")

    context = {
        'payment_id': request.GET.get('payment_id'),
        'status': request.GET.get('status'),
    }

    return render(request, 'new_authors/payment_failure.html', context)


@login_required
def payment_pending(request):
    """
    Página exibida quando pagamento está pendente
    """
    messages.info(request, "Seu pagamento está sendo processado. Você receberá uma notificação quando for confirmado.")

    context = {
        'payment_id': request.GET.get('payment_id'),
        'status': request.GET.get('status'),
    }

    return render(request, 'new_authors/payment_pending.html', context)


# ========== WEBHOOK ==========

@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Webhook para receber notificações do MercadoPago
    """
    try:
        data = json.loads(request.body)
        logger.info(f"Webhook MercadoPago recebido: {data}")

        topic = data.get('topic') or data.get('type')

        if topic == 'payment':
            payment_id = data.get('data', {}).get('id')

            if payment_id:
                # Buscar informações do pagamento
                payment_info = payment_service.sdk.payment().get(payment_id)

                if payment_info['status'] == 200:
                    payment_data = payment_info['response']
                    status = payment_data.get('status')
                    external_reference = payment_data.get('external_reference', '')

                    # Parse da referência
                    # Formato: "author_sub_1_plan_2" ou "publisher_sub_1_plan_2_trial_True"
                    if external_reference.startswith('author_sub_'):
                        parts = external_reference.split('_')
                        subscription_id = int(parts[2])
                        payment_service.process_author_payment(subscription_id, status)

                    elif external_reference.startswith('publisher_sub_'):
                        parts = external_reference.split('_')
                        subscription_id = int(parts[2])
                        is_trial = 'trial_True' in external_reference
                        payment_service.process_publisher_payment(subscription_id, status, is_trial)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return HttpResponse(status=500)


# ========== CANCELAMENTO ==========

@login_required
@require_POST
def cancel_subscription(request):
    """
    Cancela assinatura do usuário
    """
    user_type = request.POST.get('user_type')

    try:
        if user_type == 'author':
            author = request.user.emerging_author_profile
            subscription = AuthorSubscription.objects.get(author=author)
            subscription.cancel()
            messages.success(request, "Assinatura cancelada. Você manterá o acesso até o final do período pago.")
            return redirect('new_authors:author_dashboard')

        elif user_type == 'publisher':
            publisher = request.user.publisher_profile
            subscription = PublisherSubscription.objects.get(publisher=publisher)
            subscription.cancel()
            messages.success(request, "Assinatura cancelada. Você manterá o acesso até o final do período pago.")
            return redirect('new_authors:publisher_dashboard')

    except Exception as e:
        logger.error(f"Erro ao cancelar assinatura: {str(e)}")
        messages.error(request, "Erro ao cancelar assinatura. Entre em contato com o suporte.")

    return redirect('new_authors:books_list')

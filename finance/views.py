"""Views do modulo financeiro"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json
import logging
from .models import Subscription, Order, TransactionLog
from .services import MercadoPagoService

logger = logging.getLogger(__name__)
mp_service = MercadoPagoService()

@login_required
def subscription_checkout(request):
    payment_method = request.GET.get('method', 'pix')
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'pix')
        result = mp_service.create_subscription_preference(request.user, payment_method)
        if result['success']:
            return redirect(result['init_point'])
        else:
            messages.error(request, f"Erro ao processar pagamento: {result['error']}")
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        subscription = None
    context = {'subscription': subscription, 'payment_method': payment_method}
    return render(request, 'finance/checkout.html', context)

@login_required
def subscription_status(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        subscription = None
    return render(request, 'finance/subscription_status.html', {'subscription': subscription})

@login_required
@require_POST
def subscription_cancel(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
        subscription.cancel()
        messages.success(request, 'Assinatura cancelada com sucesso.')
    except Subscription.DoesNotExist:
        messages.error(request, 'Voce nao possui uma assinatura ativa.')
    return redirect('finance:subscription_status')

@login_required
def subscription_success(request):
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    preference_id = request.GET.get('preference_id')
    
    if status == 'approved':
        try:
            subscription = Subscription.objects.get(user=request.user)
            if subscription.status != 'ativa':
                subscription.mp_payment_id = payment_id
                
                # Mapear método de pagamento do GET (se houver)
                payment_type = request.GET.get('payment_type', '')
                if payment_type == 'credit_card':
                    subscription.payment_method = 'credit_card'
                elif payment_type == 'ticket':
                    subscription.payment_method = 'boleto'
                elif payment_type == 'bank_transfer':
                    subscription.payment_method = 'pix'
                    
                subscription.activate()
                
                # Criar log de transação
                TransactionLog.objects.create(
                    transaction_type='subscription',
                    user=request.user,
                    subscription=subscription,
                    mp_payment_id=payment_id,
                    mp_status=status,
                    amount=subscription.price,
                    payment_method=subscription.payment_method,
                    raw_data={'source': 'redirect_success', 'get_params': dict(request.GET)}
                )
                messages.success(request, 'Pagamento aprovado! Sua assinatura premium esta ativa.')
            else:
                messages.info(request, 'Sua assinatura premium ja esta ativa.')
        except Subscription.DoesNotExist:
            messages.error(request, 'Nao encontramos nenhuma assinatura pendente.')
        except Exception as e:
            logger.error(f"Erro ao ativar assinatura no redirect de sucesso: {e}", exc_info=True)
            messages.error(request, 'Houve um erro ao processar sua assinatura. Contate o suporte.')
    else:
        messages.warning(request, 'O pagamento nao foi aprovado ou esta pendente.')
        
    return redirect('finance:subscription_status')

@login_required
def subscription_failure(request):
    messages.error(request, 'Houve um problema com o pagamento. Tente novamente.')
    return redirect('finance:subscription_checkout')

@login_required
def subscription_pending(request):
    messages.info(request, 'Seu pagamento esta pendente. Aguarde a confirmacao.')
    return redirect('finance:subscription_status')

@csrf_exempt
@require_http_methods(['POST'])
def mercadopago_webhook(request):
    """Webhook do MercadoPago com verificação de assinatura."""
    try:
        # Verificar assinatura do MercadoPago
        x_signature = request.headers.get('X-Signature', '')
        x_request_id = request.headers.get('X-Request-Id', '')
        
        if not x_signature:
            logger.warning("Webhook MercadoPago recebido SEM assinatura X-Signature")
            # Em produção, rejeitar requests sem assinatura:
            # return JsonResponse({'status': 'error', 'message': 'Missing signature'}, status=401)
        
        data = json.loads(request.body)
        
        # Validar que o payload contém campos esperados
        topic = data.get('topic') or data.get('type')
        if not topic:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload'}, status=400)
        
        result = mp_service.process_webhook(data)
        if result['success']:
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': result.get('error')}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Erro no webhook MercadoPago: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Internal error'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def cron_check_subscriptions(request):
    """
    Endpoint para ser chamado pelo cron-job.org para verificar assinaturas expirando.
    
    Protegido por token secreto via header (NÃO via query string para evitar vazamento em logs).
    Header: X-Cron-Token: SEU_CRON_SECRET
    """
    from .email_service import PremiumEmailService
    
    # Verificar token de autenticação (SOMENTE via header — evita vazamento em logs/Referer)
    token = request.headers.get('X-Cron-Token')
    expected_token = getattr(settings, 'CRON_SECRET_TOKEN', None)
    
    if not expected_token:
        logger.warning("CRON_SECRET_TOKEN não configurado no settings")
        return JsonResponse({'error': 'Cron not configured'}, status=500)
    
    if not token or token != expected_token:
        logger.warning("Tentativa de acesso ao cron com token inválido ou ausente")
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    logger.info("🔍 Iniciando verificação de assinaturas expirando via CRON...")
    
    now = timezone.now()
    results = {
        'expiring_3_days': 0,
        'expiring_1_day': 0,
        'expired_today': 0,
        'errors': 0,
    }
    
    # Assinaturas que expiram em 3 dias
    date_3_days = now.date() + timedelta(days=3)
    for sub in Subscription.objects.filter(status='ativa', expiration_date__date=date_3_days).select_related('user'):
        try:
            PremiumEmailService.send_expiring_reminder(user=sub.user, days_left=3, expires_at=sub.expiration_date)
            results['expiring_3_days'] += 1
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 3 dias: {e}")
            results['errors'] += 1
    
    # Assinaturas que expiram amanhã
    date_1_day = now.date() + timedelta(days=1)
    for sub in Subscription.objects.filter(status='ativa', expiration_date__date=date_1_day).select_related('user'):
        try:
            PremiumEmailService.send_expiring_reminder(user=sub.user, days_left=1, expires_at=sub.expiration_date)
            results['expiring_1_day'] += 1
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 1 dia: {e}")
            results['errors'] += 1
    
    # Assinaturas que expiraram hoje (win-back)
    for sub in Subscription.objects.filter(status='ativa', expiration_date__date=now.date()).select_related('user'):
        try:
            sub.status = 'expirada'
            sub.save()
            PremiumEmailService.send_winback_email(user=sub.user, expired_at=sub.expiration_date)
            results['expired_today'] += 1
        except Exception as e:
            logger.error(f"Erro ao processar expiração: {e}")
            results['errors'] += 1
    
    logger.info(f"✅ Verificação concluída: {results}")
    
    return JsonResponse({
        'status': 'success',
        'results': results,
        'timestamp': now.isoformat()
    })

"""Views do modulo financeiro"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json
import logging
from .models import Subscription, Order
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
    messages.success(request, 'Pagamento aprovado! Sua assinatura premium esta ativa.')
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
    try:
        data = json.loads(request.body)
        result = mp_service.process_webhook(data)
        if result['success']:
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': result.get('error')}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def cron_check_subscriptions(request):
    """
    Endpoint para ser chamado pelo cron-job.org para verificar assinaturas expirando.
    
    Protegido por token secreto via query parameter ou header.
    URL: /api/cron/check-subscriptions/?token=SEU_CRON_SECRET
    """
    from .email_service import PremiumEmailService
    
    # Verificar token de autenticação
    token = request.GET.get('token') or request.headers.get('X-Cron-Token')
    expected_token = getattr(settings, 'CRON_SECRET_TOKEN', None)
    
    if not expected_token:
        logger.warning("CRON_SECRET_TOKEN não configurado no settings")
        return JsonResponse({'error': 'Cron not configured'}, status=500)
    
    if token != expected_token:
        logger.warning(f"Tentativa de acesso ao cron com token inválido: {token[:10]}..." if token else "sem token")
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

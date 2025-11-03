"""Views do modulo financeiro"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
import json
from .models import Subscription, Order
from .services import MercadoPagoService

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

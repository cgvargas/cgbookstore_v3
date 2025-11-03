"""
URLs do modulo financeiro
"""
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('subscription/checkout/', views.subscription_checkout, name='subscription_checkout'),
    path('subscription/status/', views.subscription_status, name='subscription_status'),
    path('subscription/cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('subscription/failure/', views.subscription_failure, name='subscription_failure'),
    path('subscription/pending/', views.subscription_pending, name='subscription_pending'),
    path('webhook/mercadopago/', views.mercadopago_webhook, name='mercadopago_webhook'),
]

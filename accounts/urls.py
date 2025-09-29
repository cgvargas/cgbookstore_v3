from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # /contas/login/ -> Usa a view pronta do Django
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),

    # /contas/logout/ -> Usa a view pronta do Django
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    # /contas/registrar/ -> Usa a nossa view customizada
    path('registrar/', views.register_view, name='register'),
]
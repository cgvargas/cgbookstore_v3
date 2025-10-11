from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('registrar/', views.register_view, name='register'),

    # URLs DO PERFIL
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('profile/upload-banner/', views.upload_banner, name='upload_banner'), # <-- VERIFIQUE ESTA LINHA
    path('profile/update-theme/', views.update_theme, name='update_theme'),
]
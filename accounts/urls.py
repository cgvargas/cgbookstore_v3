from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs DO PERFIL
    path('edit/', views.edit_profile, name='edit_profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('upload-banner/', views.upload_banner, name='upload_banner'),
    path('update-theme/', views.update_theme, name='update_theme'),
    path('update-banner-position/', views.update_banner_position, name='update_banner_position'),

    # URLs de Background Personalizado (PREMIUM)
    path('upload-background/', views.upload_background, name='upload_background'),
    path('update-background-settings/', views.update_background_settings, name='update_background_settings'),
    path('remove-background/', views.remove_background, name='remove_background'),

    # URLs de Exclusão de Conta
    path('delete-account/confirm/', views.delete_account_confirm, name='delete_account_confirm'),
    path('delete-account/', views.delete_account, name='delete_account'),

    # URLs de Autenticação (LEGADO - mantidas por compatibilidade)
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
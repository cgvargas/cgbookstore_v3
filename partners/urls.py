from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('redirect/book/<int:book_id>/partner/<int:partner_id>/', views.redirect_to_partner, name='redirect_to_partner'),
    path('redirect/book/<int:book_id>/', views.redirect_to_partner, name='redirect_to_partner_no_id'),
]

"""
Rotas do módulo Product Analytics.
"""
from django.urls import path
from . import views

app_name = "product_analytics"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
]

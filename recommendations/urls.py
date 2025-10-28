"""
URLs para a API de Recomendações.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_simple

app_name = 'recommendations'

# Router para ViewSets
router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='profile')
router.register(r'interactions', views.UserBookInteractionViewSet, basename='interactions')

urlpatterns = [
    # ViewSets
    path('api/', include(router.urls)),

    # Function-based views (Django puro - SEM DRF)
    path('api/recommendations/', views_simple.get_recommendations_simple, name='get_recommendations'),

    # Function-based views (DRF - caso precise)
    path('api/recommendations-drf/', views.get_recommendations, name='get_recommendations_drf'),
    path('api/books/<int:book_id>/similar/', views.get_similar_books, name='similar_books'),
    path('api/recommendations/<int:recommendation_id>/click/', views.track_recommendation_click, name='track_click'),
    path('api/insights/', views.get_user_insights, name='user_insights'),
]

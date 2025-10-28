"""
Admin para o Sistema de Recomendações.
"""
from django.contrib import admin
from .models import UserProfile, UserBookInteraction, BookSimilarity, Recommendation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_books_read', 'total_pages_read', 'created_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserBookInteraction)
class UserBookInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'interaction_type', 'rating', 'created_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['interaction_type', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(BookSimilarity)
class BookSimilarityAdmin(admin.ModelAdmin):
    list_display = ['book_a', 'book_b', 'similarity_score', 'method', 'updated_at']
    search_fields = ['book_a__title', 'book_b__title']
    list_filter = ['method', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'recommendation_type', 'score', 'is_clicked', 'expires_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['recommendation_type', 'is_clicked', 'created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'clicked_at']

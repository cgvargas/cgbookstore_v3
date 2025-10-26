from django.contrib import admin
from .models import DebateTopic, DebatePost, DebateVote


@admin.register(DebateTopic)
class DebateTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'book', 'creator', 'posts_count', 'views_count', 'is_pinned', 'is_locked', 'created_at']
    list_filter = ['is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'description', 'book__title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'posts_count']
    list_per_page = 20


@admin.register(DebatePost)
class DebatePostAdmin(admin.ModelAdmin):
    list_display = ['author', 'topic', 'votes_score', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['content', 'author__username', 'topic__title']
    readonly_fields = ['created_at', 'edited_at', 'votes_score']
    list_per_page = 50


@admin.register(DebateVote)
class DebateVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    list_per_page = 50
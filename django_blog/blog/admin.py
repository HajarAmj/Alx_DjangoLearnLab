from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('published_date',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'author')
    search_fields = ('content', 'author__username', 'post__title')

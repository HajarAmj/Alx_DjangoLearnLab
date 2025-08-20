from django.urls import path
from .views import UserLoginView, UserLogoutView, register, profile, profile_edit
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView
)
app_name = "blog"

urlpatterns = [
    # Authentication URLs
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),

    # Blog post URLs
    path('posts/', PostListView.as_view(), name='post-list'),              # list view can stay plural
    path('post/new/', PostCreateView.as_view(), name='post-create'),       # singular 'post/'
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),  # singular 'post/'
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'), 
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    # Comment URLs
    path("post/<int:pk>/comments/new/", views.CommentCreateView.as_view(), name="comment_create"),
    path("comment/<int:pk>/update/", views.CommentUpdateView.as_view(), name="comment_update"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
]


from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, FeedView
from .views import like_post, unlike_post

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('feed/', FeedView.as_view(), name='user-feed'),
    path('<int:pk>/like/', like_post, name='like-post'),
    path('<int:pk>/unlike/', unlike_post, name='unlike-post'),  
]

urlpatterns += router.urls

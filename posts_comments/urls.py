from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PostViewSet, CommentViewSet

posts_router = SimpleRouter()
posts_router.register(prefix='', viewset=PostViewSet, basename='api_posts')
comments_router = SimpleRouter()
comments_router.register(prefix='', viewset=CommentViewSet, basename='api_comments')
# prefix is for the url, basename for the url name

urlpatterns = [
    path('', include(posts_router.urls)),
    path('comments/', include(comments_router.urls))
]

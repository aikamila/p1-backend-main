from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserView, InitialVerifyEmailView, TokenBlacklistView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('registration/', UserView.as_view({'post': 'create'}), name='api_user_creation'),
    path('<int:pk>/', UserView.as_view({'get': 'retrieve'}), name='api_user'),
    path('token/verification/', InitialVerifyEmailView.as_view(), name='api_initial_email_verification')
]

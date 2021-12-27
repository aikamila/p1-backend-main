from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateUserView, InitialVerifyEmailView, TokenBlacklistView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('user-creation', CreateUserView.as_view(), name='api_user_creation'),
    path('initial-email-verification', InitialVerifyEmailView.as_view(), name='api_initial_email_verification')
]
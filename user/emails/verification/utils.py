from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


class InitEmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Overriding a Django class responsible for generating pw reset
    tokens in order to create tokens for initial email verification
    """
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.id) + str(timestamp) + str(user.email) + str(user.is_active)
        )


initial_email_verification_token_generator = InitEmailVerificationTokenGenerator()


class EmailVerificationUtils:
    """
    A class responsible for providing utilities that are necessary during:
    1. User initial email verification
    2. Password reset email verification
    """
    @staticmethod
    def encode_user(user):
        return urlsafe_base64_encode(force_bytes(user.id))

    @staticmethod
    def decode_user(uid):
        _user = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = _user.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, _user.DoesNotExist):
            user = None
        return user

    @staticmethod
    def obtain_tokens(user):
        if user is not None:
            refresh = RefreshToken.for_user(user=user)
            access = refresh.access_token
            return {'refresh': str(refresh), 'access': str(access)}
        return {}




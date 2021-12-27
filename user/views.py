from .serializers import CreateUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails.verification.utils import EmailVerificationUtils, initial_email_verification_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import TokenError, TokenBackendError


class CreateUserView(APIView):
    """
    Creating a user account if the data is valid. Sending a
    verification email.
    """
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InitialVerifyEmailView(APIView):
    """
    Activation of the user's account. If credentials provided in
    the request are valid, response contains a pair of JWT tokens
    """
    def post(self, request):
        try:
            id = request.data['id']
            token = request.data['token']
        except KeyError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        if id and token:
            user = EmailVerificationUtils.decode_user(id)
            if user is not None and initial_email_verification_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                data = EmailVerificationUtils.obtain_tokens(user)
                return Response(data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class TokenBlacklistView(APIView):
    """
    If the token passed in a request is valid, it is blacklisted.
    """
    def post(self, request):
        try:
            refresh = request.data['refresh']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh_token = RefreshToken(refresh)
        except (TokenError, TokenBackendError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        refresh_token.blacklist()
        return Response(status=status.HTTP_200_OK)

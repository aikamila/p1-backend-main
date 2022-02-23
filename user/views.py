from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails.verification.utils import EmailVerificationUtils, initial_email_verification_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import TokenError, TokenBackendError
from rest_framework import viewsets
from .custom_permissions import UserViewPermission
from django.contrib.auth import get_user_model


class UserView(viewsets.ViewSet):
    permission_classes = [UserViewPermission]

    def create(self, request):
        """
        Creating a user account if the data is valid. Sending a
        verification email.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Responds with user's data or 404 if the user doesn't exist/is inactive.
        """
        user_model = get_user_model()
        try:
            user = user_model.objects.get(pk=pk)
        except user_model.DoesNotExist:
            return Response({'message': 'This user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response({'message': 'This user is not active.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InitialVerifyEmailView(APIView):
    """
    Activation of the user's account. If credentials provided in
    the request are valid, the response contains a pair of JWT tokens
    """
    def post(self, request):
        try:
            pk = request.data['id']
            token = request.data['token']
        except KeyError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        if pk and token:
            user = EmailVerificationUtils.decode_user(pk)
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

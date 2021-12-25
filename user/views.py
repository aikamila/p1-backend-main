from .serializers import CreateUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails.verification.utils import EmailVerificationUtils, initial_email_verification_token_generator


class CreateUserView(APIView):
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


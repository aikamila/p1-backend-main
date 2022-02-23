from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from ...emails.verification.utils import EmailVerificationUtils


class TokenBlacklistViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('token_blacklist')
        my_user = get_user_model()
        user = my_user.objects.create_user(name='Testing',
                                           surname='Testing',
                                           username='UserOne',
                                           password='SecretPassword',
                                           email='test@test.com')
        user.is_active = True
        user.save()
        user.refresh_from_db()
        tokens = EmailVerificationUtils.obtain_tokens(user)
        self.refresh_token = tokens['refresh']

    def test_key_error(self):
        """
        Invalid request
        """
        data = {'id': 39988}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        """
        Invalid token is sent in the request
        """
        data = {'refresh': "testing_invalid"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {'refresh': str(self.refresh_token) + 'e'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_and_already_blacklisted_token(self):
        """
        1. Valid token is sent in the request
        2. Token that has already been used is sent in the request
        """
        data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




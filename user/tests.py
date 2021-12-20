from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import MyUser
from rest_framework import status
from django.core import mail


class JWTViewsTest(APITestCase):
    def setUp(self):
        self.url = reverse('token_obtain_pair')
        self.user = MyUser.objects.create_user(email='test@test.com',
                                               username='test_user',
                                               name='Testname',
                                               surname='Testsurname',
                                               password='test_password')

    def test_user_inactive(self):
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'password': 'test_password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_active(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'password': 'test_password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        refresh = response.data['refresh']
        url = reverse('token_refresh')
        second_response = self.client.post(url, {'refresh': refresh},
                                           format='json')
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in second_response.data)
        third_response = self.client.post(url, {'refresh': str(refresh) + 'a'},
                                          format='json')
        self.assertEqual(third_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_invalid_credentials(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post(self.url, {'email': 'tet@test.com',
                                               'password': 'test_password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateUserAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('api_user_creation')

    def test_proper_user_creation(self):
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'name': 'Test',
                                               'surname': 'Test',
                                               'username': 'UserOne',
                                               'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# various cases for improper user creation - should have been written before with
# the first test as you use tdd for this project

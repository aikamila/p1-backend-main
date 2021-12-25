from rest_framework.test import APITestCase
from django.urls import reverse
from ...models import MyUser
from rest_framework import status
from django.core import mail
from ...serializers import CreateUserSerializer
from django.contrib.auth import get_user_model
from django.conf import settings
from ...emails.verification.utils import initial_email_verification_token_generator, EmailVerificationUtils


class CreateUserAPITest(APITestCase):
    """
    Testing of user creation - without testing verification emails
    """
    def setUp(self):
        self.url = reverse('api_user_creation')

    def test_invalid_user_creation_not_unique_username(self):
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'name': 'Test',
                                               'surname': 'Test',
                                               'username': 'UserOne',
                                               'password': 'password',
                                               'bio': 'Hi everyone!'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, {'email': 'testtest@test.com',
                                               'name': 'Test',
                                               'surname': 'Test',
                                               'username': 'UserOne',
                                               'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"username": ["my user with this username already exists."]})

    def test_invalid_user_creation_not_unique_email(self):
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'name': 'Test',
                                               'surname': 'Test',
                                               'username': 'UserOne',
                                               'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, {'email': 'test@test.com',
                                               'name': 'Test',
                                               'surname': 'Test',
                                               'username': 'UserSecond',
                                               'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"email": ["my user with this email already exists."]})

    def test_invalid_user_creation_not_all_fields(self):
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'surname': 'Test',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['name']))
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'Testing',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['surname']))
        serializer = CreateUserSerializer(data={'name': 'Testing',
                                                'surname': 'Test',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['email']))
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'Testing',
                                                'surname': 'Test',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['username']))
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'Testing',
                                                'surname': 'Test',
                                                'username': 'UserOne'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['password']))

    def test_invalid_email_user_creation(self):
        serializer = CreateUserSerializer(data={'email': 'test.com',
                                                'name': 'Testing',
                                                'surname': 'Test',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['email']))

    def test_invalid_name_user_creation(self):
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'testing',
                                                'surname': 'Test',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['name']))

    def test_invalid_surname_user_creation(self):
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'Testing',
                                                'surname': 'test',
                                                'username': 'UserOne',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['surname']))

    def test_invalid_username_user_creation(self):
        serializer = CreateUserSerializer(data={'email': 'test@test.com',
                                                'name': 'Testing',
                                                'surname': 'Test',
                                                'username': '<script>',
                                                'password': 'password'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['username']))


class CreateAndVerifyUsersEmailTest(APITestCase):
    """
    Testing of the entire creating-verification of users flow
    """
    def setUp(self):
        self.url_create = reverse('api_user_creation')
        self.url_verify = reverse('api_initial_email_verification')

    def test_create_invalid(self):
        response = self.client.post(self.url_create, {'email': 'testtest@test.com',
                                                      'name': 'test',
                                                      'surname': 'Test',
                                                      'username': 'UserOne',
                                                      'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = get_user_model()
        self.assertEqual(len(user.objects.all()), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_create_valid(self):
        response = self.client.post(self.url_create, {'email': 'testtest@test.com',
                                                      'name': 'Test',
                                                      'surname': 'Test',
                                                      'username': 'UserOne',
                                                      'password': 'password'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model()
        self.assertEqual(len(user.objects.all()), 1)
        self.assertEqual(len(mail.outbox), 1)
        user_object = user.objects.get(name='Test')
        self.assertEqual(user_object.is_active, False)
        self.assertEqual(mail.outbox[0].to, [user_object.email])
        self.assertEqual(mail.outbox[0].from_email, settings.EMAIL_HOST_USER)
        valid_token = mail.outbox[0].body.split('/')[-2]
        valid_id_encoded = mail.outbox[0].body.split('/')[-3]
        id_encoded = EmailVerificationUtils.encode_user(user_object)
        self.assertEqual(valid_id_encoded, id_encoded)
        response = self.client.post(self.url_verify, {'id': valid_id_encoded,
                                                      'token': str(valid_token) + 'i'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(user_object.is_active, False)
        response = self.client.post(self.url_verify, {'id': str(valid_id_encoded) + 'i',
                                                      'token': str(valid_token)},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.url_verify, {'id': str(valid_id_encoded)},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url_verify, {'id': str(valid_id_encoded),
                                                      'token': str(valid_token)},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        user_object.refresh_from_db()
        self.assertTrue(user_object.is_active, True)
        response = self.client.post(self.url_verify, {'id': str(valid_id_encoded),
                                                      'token': str(valid_token)},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



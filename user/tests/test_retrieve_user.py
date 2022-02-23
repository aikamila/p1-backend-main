from rest_framework.test import APITestCase
from django.shortcuts import reverse
from ..models import MyUser
from rest_framework import status


class UserRetrieveTest(APITestCase):
    def setUp(self) -> None:
        user1_data = {
            "name": "First",
            "surname": "User",
            "username": "User1",
            "password": "Password",
            "email": "testemail@test.test"
        }

        user2_data = {
            "name": "Second",
            "surname": "User",
            "username": "User2",
            "password": "Password",
            "email": "testemail2@test.test",
            "bio": "That's me"
        }

        user3_data = {
            "name": "Third",
            "surname": "User",
            "username": "User3",
            "password": "Password",
            "email": "testemail3@test.test",
            "bio": "That's me"
        }

        token_url = reverse('token_obtain_pair')

        user1 = MyUser.objects.create_user(**user1_data)
        user1.is_active = True
        user1.save()

        user2 = MyUser.objects.create_user(**user2_data)
        user2.is_active = True
        user2.save()

        MyUser.objects.create_user(**user3_data)

        self.token_user1 = self.client.post(token_url, {
            "email": user1.email,
            "password": "Password"
        }).data.get("access")

    def test_unauthorized_user(self):
        """
        User without a token cannot access this endpoint.
        """
        self.client.credentials()
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id-1]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user(self):
        """
        User with a token can access both info about themselves
        and other users.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id - 2]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id - 1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_does_not_exist(self):
        """
        If the given user doesn't exist, the server should respond with
        404 response.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id + 1]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'This user does not exist.'})

    def test_user_is_inactive(self):
        """
        Server responds with 404 response if the given user is inactive.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'This user is not active.'})

    def test_response_is_valid(self):
        """
        The 200 response contains valid data.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id - 1]))
        expected_response = {
            "username": "User2",
            "id": MyUser.objects.latest("id").id - 1,
            "email": "testemail2@test.test",
            "name": "Second",
            "surname": "User",
            "bio": "That's me"
        }
        self.assertEqual(response.data, expected_response)
        response = self.client.get(reverse('api_user', args=[MyUser.objects.latest('id').id - 2]))
        expected_response = {
            "username": "User1",
            "id": MyUser.objects.latest("id").id - 2,
            "email": "testemail@test.test",
            "name": "First",
            "surname": "User",
            "bio": ''
        }
        self.assertEqual(response.data, expected_response)

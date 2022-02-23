from rest_framework.test import APITestCase
from django.shortcuts import reverse
from user.models import MyUser
from posts_comments.models import Post
from django.utils.timezone import now
from rest_framework import status
from datetime import timedelta


class CreatePostTest(APITestCase):
    def setUp(self) -> None:
        user1_data = {
            "name": "First",
            "surname": "User",
            "username": "User1",
            "password": "Password",
            "email": "testemail@test.test"
        }

        token_url = reverse('token_obtain_pair')

        user1 = MyUser.objects.create_user(**user1_data)
        user1.is_active = True
        user1.save()

        self.token_user1 = self.client.post(token_url, {
            "email": user1.email,
            "password": "Password"
        }).data.get("access")

        Post.objects.create(user=user1, text="Valid post valid post valid post.", time=now() - timedelta(hours=1))

    def test_user_not_authenticated(self):
        self.client.credentials()
        url = reverse('api_posts-basic_info', args=[Post.objects.latest("id").id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-basic_info', args=[Post.objects.latest("id").id + 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This post doesn't exist"})

    def test_valid_data_in_response(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-basic_info', args=[Post.objects.latest("id").id])
        response = self.client.get(url)
        expected_data = {
            "id": Post.objects.latest("id").id,
            "user": {
                "username": "User1",
                "id": MyUser.objects.latest("id").id
            },
            "text": "Valid post valid post valid post.",
            "time_since_posted": "1 hour ago"
        }
        self.assertEqual(response.data, expected_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



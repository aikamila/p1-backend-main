from rest_framework.test import APITestCase
from rest_framework import status
from user.models import MyUser
from posts_comments.models import Post
from django.shortcuts import reverse
from django.utils import timezone
from datetime import timedelta

# 100 %


class ListPostsTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('api_posts-list')
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
            "email": "testemail2@test.test"
        }

        token_url = reverse('token_obtain_pair')

        user1 = MyUser.objects.create_user(**user1_data)
        user1.is_active = True
        user1.save()

        user2 = MyUser.objects.create_user(**user2_data)
        user2.is_active = True
        user2.save()

        post1 = Post.objects.create(user=user1, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1", time=timezone.now() - timedelta(days=3))
        Post.objects.create(user=user2, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 2", time=timezone.now() - timedelta(days=2))
        post1.engagement_rate = 6
        post1.save()

        self.token_user1 = self.client.post(token_url, {
            "email": user1.email,
            "password": "Password"
        }).data.get("access")

    def test_unauthorized_user(self):
        """
        Making sure that users without a token cannot access the endpoint.
        """
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user(self):
        """
        Making sure that users with a token can access proper data
        in a proper order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": Post.objects.latest("id").id,
                "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 2",
                "user": {
                    "username": "User2",
                    "id": MyUser.objects.latest("id").id
                },
                "time_since_posted": "2 days ago",
                "engagement_rate": 0
            },
            {
                "id": Post.objects.latest("id").id - 1,
                "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1",
                "user": {
                    "username": "User1",
                    "id": MyUser.objects.latest("id").id - 1
                },
                "time_since_posted": "3 days ago",
                "engagement_rate": 6
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_filtered_posts(self):
        """
        Filtering posts using user id works correctly
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(f"{self.url}?user__id={MyUser.objects.latest('id').id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": Post.objects.latest("id").id,
                "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 2",
                "user": {
                    "username": "User2",
                    "id": MyUser.objects.latest("id").id
                },
                "time_since_posted": "2 days ago",
                "engagement_rate": 0
            }
        ]
        self.assertEqual(response.data, expected_data)

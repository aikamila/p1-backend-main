import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import MyUser
from posts_comments.models import Post
from django.shortcuts import reverse
from django.utils import timezone
from datetime import timedelta
from ...serializers import PostCreateUpdateSerializer

# 100 %


class CreatePostTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('api_posts-list')
        user1_data = {
            "name": "First",
            "surname": "User",
            "username": "User1",
            "password": "Password",
            "email": "testemail@test.test"
        }

        token_url = reverse('token_obtain_pair')

        self.user1 = MyUser.objects.create_user(**user1_data)
        self.user1.is_active = True
        self.user1.save()
        self.token_user1 = self.client.post(token_url, {
            "email": self.user1.email,
            "password": "Password"
        }).data.get("access")

    def test_unauthorized_user(self):
        """
        Making sure that users without a token cannot access the endpoint.
        """
        self.client.credentials()
        data = {
            "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_data(self):
        """
        Making sure that the server responds with 400 in case of
        invalid data being sent.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "text": "a" * 5001
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_too_short(self):
        """
        Min. length of a post should be 30 characters
        """
        serializer = PostCreateUpdateSerializer(data={'text': 'too short'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['text']))

    def test_valid_data(self):
        """
        Testing the behavior of the server in case of valid data being sent.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.latest("id").text, "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1")
        self.assertEqual(Post.objects.latest("id").user, self.user1)
        self.assertEqual(Post.objects.latest("id").engagement_rate, 0)
        self.assertTrue(Post.objects.latest("id").time < timezone.now())
        self.assertTrue(Post.objects.latest("id").time + timedelta(seconds=2) > timezone.now())

    def test_valid_data_plus_extra_data(self):
        """
        Testing the behavior in case of some additional data like time or engagement
        rate being sent.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        data = {
            "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1",
            "engagement_rate": 6,
            "time": datetime.datetime(year=2222, month=7, day=4)
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.latest("id").text, "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1")
        self.assertEqual(Post.objects.latest("id").user, self.user1)
        self.assertEqual(Post.objects.latest("id").engagement_rate, 0)
        self.assertTrue(Post.objects.latest("id").time < timezone.now())
        self.assertTrue(Post.objects.latest("id").time + timedelta(seconds=2) > timezone.now())

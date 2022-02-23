from rest_framework.test import APITestCase
from user.models import MyUser
from posts_comments.models import Post
from django.shortcuts import reverse
from django.utils import timezone
from rest_framework import status

# 100 %


class UpdatePostTest(APITestCase):
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
            "email": "testemail2@test.test"
        }
        token_url = reverse('token_obtain_pair')

        self.user1 = MyUser.objects.create_user(**user1_data)
        self.user1.is_active = True
        self.user1.save()

        self.user2 = MyUser.objects.create_user(**user2_data)
        self.user2.is_active = True
        self.user2.save()

        self.post = Post.objects.create(user=self.user1, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1", time=timezone.now())
        self.time = self.post.time

        self.token_user1 = self.client.post(token_url, {
            "email": self.user1.email,
            "password": "Password"
        }).data.get("access")

        self.token_user2 = self.client.post(token_url, {
            "email": self.user2.email,
            "password": "Password"
        }).data.get("access")

    def test_unauthorized_user(self):
        """
        Making sure that users without a token cannot access the endpoint.
        """
        self.client.credentials()
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        data = {
            'text': "Updated Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_does_not_exist_404_response(self):
        """
        Checking the status and content of the response when a post with
        the given pk doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id + 1])
        data = {
            'text': "Updated Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This post doesn't exist"})

    def test_user_unauthorised_to_update_a_post(self):
        """
        Making sure that users other than the author cannot update a post.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        data = {
            'text': "Updated Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_authorised_to_update_a_post(self):
        """
        Making sure that the author can update their post and the post is
        updated in a proper way.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        data = {
            'text': "Updated Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, "Updated Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1")
        self.assertEqual(self.post.time, self.time)
        self.assertEqual(self.post.user.id, MyUser.objects.latest("id").id - 1)
        self.assertEqual(self.post.engagement_rate, 0)

    def test_invalid_request(self):
        """
        Making sure that in case of invalid data being sent, the server responds with
        400 response.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        data = {
            'text': "k"*5001
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1")

from rest_framework.test import APITestCase
from posts_comments.models import Post, Comment, Reply
from user.models import MyUser
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import reverse
from rest_framework import status

# 100%


class DeletePostTest(APITestCase):
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

        user1 = MyUser.objects.create_user(**user1_data)
        user1.is_active = True
        user1.save()

        user2 = MyUser.objects.create_user(**user2_data)
        user2.is_active = True
        user2.save()
        post = Post.objects.create(user=user1, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1", time=timezone.now() - timedelta(days=3))
        comment1 = Comment.objects.create(post=post, user=user2, time=timezone.now() - timedelta(days=1),
                                          text="Comment 1")
        Reply.objects.create(comment=comment1, user=user1, time=timezone.now() - timedelta(hours=1),
                             text="Reply 1")

        self.token_user1 = self.client.post(token_url, {
            "email": user1.email,
            "password": "Password"
        }).data.get("access")

        self.token_user2 = self.client.post(token_url, {
            "email": user2.email,
            "password": "Password"
        }).data.get("access")

    def test_unauthorized_user(self):
        """
        Making sure that users without a token cannot access the endpoint.
        """
        self.client.credentials()
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_does_not_exist_404_response(self):
        """
        Checking the status and content of the response when a post with
        the given pk doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id + 1])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This post doesn't exist"})

    def test_user_unauthorized_to_delete_a_post(self):
        """
        Making sure that users other than the author cannot delete a post.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_authorized_to_delete_a_post(self):
        """
        Making sure that the author can delete their own post and all
        related comments and replies are deleted too.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-detail', args=[Post.objects.latest('id').id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(Reply.objects.count(), 0)

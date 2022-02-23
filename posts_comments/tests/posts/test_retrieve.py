from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from user.models import MyUser
from posts_comments.models import Post, Comment, Reply
from django.utils import timezone
from datetime import timedelta

# 100%


class RetrievePostTest(APITestCase):
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
        self.first_url = reverse('api_posts-detail', args=[1])
        token_url = reverse('token_obtain_pair')

        user1 = MyUser.objects.create_user(**user1_data)
        user1.is_active = True
        user1.save()

        user2 = MyUser.objects.create_user(**user2_data)
        user2.is_active = True
        user2.save()
        post = Post.objects.create(user=user1, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1", time=timezone.now()-timedelta(days=3))
        comment1 = Comment.objects.create(post=post, user=user2, time=timezone.now()-timedelta(days=1),
                                          text="Comment 1")
        Comment.objects.create(post=post, user=user1, time=timezone.now()-timedelta(days=2),
                               text="Comment 2")
        Reply.objects.create(comment=comment1, user=user1, time=timezone.now()-timedelta(hours=1),
                             text="Reply 1")
        Reply.objects.create(comment=comment1, user=user2, time=timezone.now()-timedelta(hours=12),
                             text="Reply 2")

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
        response = self.client.get(self.first_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user(self):
        """
        Checking that both the author of a post and other users can access
        the data (when authorized with a token).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_posts-detail', args=[Post.objects.latest('id').id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.get(reverse('api_posts-detail', args=[Post.objects.latest('id').id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_does_not_exist_404_response(self):
        """
        Checking the status and content of the response when a post with
        the given pk doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_posts-detail', args=[Post.objects.latest('id').id + 1]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        response = self.client.get(reverse('api_posts-detail', args=[Post.objects.latest('id').id + 1]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This post doesn't exist"})

    def test_response_content(self):
        """
        Making sure that the 200 response contains expected data in
        appropriate order.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(reverse('api_posts-detail', args=[Post.objects.latest('id').id]))
        user_id_latest = MyUser.objects.latest('id').id
        comment_id_latest = Comment.objects.latest('id').id
        reply_id_latest = Reply.objects.latest('id').id
        expected_response = {
            "user": {
                "username": "User1",
                "id": user_id_latest-1
            },
            "text": "Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrr 1",
            "time_since_posted": "3 days ago",
            "comments": [
                {
                    "id": comment_id_latest,
                    "user": {
                        "username": "User1",
                        "id": user_id_latest-1
                    },
                    "text": "Comment 2",
                    "time_since_posted": "2 days ago",
                    "replies": []
                },
                {
                    "id": comment_id_latest-1,
                    "user": {
                        "username": "User2",
                        "id": user_id_latest
                    },
                    "text": "Comment 1",
                    "time_since_posted": "1 day ago",
                    "replies": [
                        {
                            "id": reply_id_latest,
                            "user": {
                                "username": "User2",
                                "id": user_id_latest
                            },
                            "text": "Reply 2",
                            "time_since_posted": "12 hours ago"
                        },
                        {
                            "id": reply_id_latest-1,
                            "user": {
                                "username": "User1",
                                "id": user_id_latest-1
                            },
                            "text": "Reply 1",
                            "time_since_posted": "1 hour ago"
                        }
                    ]
                }
            ]
        }
        self.assertEqual(response.data, expected_response)

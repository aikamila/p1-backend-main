import datetime
from rest_framework.test import APITestCase
from user.models import MyUser
from posts_comments.models import Post, Comment, Reply
from django.shortcuts import reverse
from django.utils import timezone
from rest_framework import status

# 100%


class CreateReplyTest(APITestCase):
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
        self.comment = Comment.objects.create(post=self.post, user=self.user2, text="Comment 1",
                                              time=timezone.now())

        self.post.refresh_from_db()

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
        url = reverse('api_comments-add_reply', args=[Comment.objects.latest("id").id])
        data = {
            'text': "Reply 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_does_not_exist_404_response(self):
        """
        Checking the status and content of the response when a comment with
        the given pk doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_comments-add_reply', args=[Comment.objects.latest("id").id + 1])
        data = {
            'text': "Reply 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This comment doesn't exist"})

    def test_invalid_data_sent_400_response(self):
        """
        Testing the response in case of providing invalid data in a POST request.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_comments-add_reply', args=[Comment.objects.latest("id").id])
        data = {
            'text': "a" * 5001
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_of_the_post_posts_a_reply(self):
        """
        Making sure that the author can post a reply under their own post
        but the engagement rate on the post doesn't grow in this way.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_comments-add_reply', args=[Comment.objects.latest("id").id])
        self.assertEqual(self.post.engagement_rate, 1)
        data = {
            'text': "Reply 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.engagement_rate, 1)
        self.assertEqual(self.comment.replies.count(), 1)
        created_reply = Reply.objects.latest("id")
        self.assertEqual(created_reply.comment, self.comment)
        self.assertEqual(created_reply.comment.post, self.post)
        self.assertEqual(created_reply.text, "Reply 1")
        self.assertEqual(created_reply.user.id, MyUser.objects.latest("id").id - 1)
        self.assertTrue(created_reply.time + datetime.timedelta(seconds=3) > timezone.now())
        self.assertTrue(created_reply.time < timezone.now())

    def test_another_user_posts_a_reply(self):
        """
        Making sure that users other than the author of the post can post
        replies and when it happens, engagement rate on the post grows.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        url = reverse('api_comments-add_reply', args=[Comment.objects.latest("id").id])
        self.assertEqual(self.post.engagement_rate, 1)
        data = {
            'text': "Reply 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.engagement_rate, 2)
        self.assertEqual(self.comment.replies.count(), 1)
        created_reply = Reply.objects.latest("id")
        self.assertEqual(created_reply.comment, self.comment)
        self.assertEqual(created_reply.comment.post, self.post)
        self.assertEqual(created_reply.text, "Reply 1")
        self.assertEqual(created_reply.user.id, MyUser.objects.latest("id").id)
        self.assertTrue(created_reply.time + datetime.timedelta(seconds=3) > timezone.now())
        self.assertTrue(created_reply.time < timezone.now())
        last_id = Reply.objects.latest("id").id
        self.assertEqual(response.data, {"text": "Reply 1", "id": last_id})

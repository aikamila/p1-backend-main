import datetime
from rest_framework.test import APITestCase
from user.models import MyUser
from posts_comments.models import Post, Comment
from django.shortcuts import reverse
from django.utils import timezone
from rest_framework import status

# 100 %


class CreateCommentTest(APITestCase):
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

        self.post = Post.objects.create(user=self.user1, text="Post numberrrrrrrrrrrrrrrrrrrrrrrrrrrrr 1", time=timezone.now())

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
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id])
        data = {
            'text': "Comment number 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_does_not_exist_404_response(self):
        """
        Checking the status and content of the response when a post with
        the given pk doesn't exist.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id + 1])
        data = {
            'text': "Comment 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': "This post doesn't exist"})

    def test_invalid_data_sent_400_response(self):
        """
        Testing the response in case of providing invalid data in a POST request
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id])
        long_str = "j"*5001
        data = {
            'text': long_str
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'text': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_posts_a_comment(self):
        """
        Making sure that the author can post a comment under their own post
        but the engagement rate on the post doesn't grow in this way.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        self.assertEqual(self.post.engagement_rate, 0)
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id])
        data = {
            'text': "Comment 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.engagement_rate, 0)
        self.assertEqual(self.post.comments.count(), 1)
        created_comment = Comment.objects.latest("id")
        self.assertEqual(created_comment.post, self.post)
        self.assertEqual(created_comment.text, "Comment 1")
        self.assertEqual(created_comment.user.id, MyUser.objects.latest("id").id - 1)
        self.assertTrue(created_comment.time + datetime.timedelta(seconds=3) > timezone.now())
        self.assertTrue(created_comment.time < timezone.now())

    def test_another_user_posts_a_comment(self):
        """
        Making sure that users other than the author can post comments
        and when it happens, engagement rate on the post grows.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        self.assertEqual(self.post.engagement_rate, 0)
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id])
        data = {
            'text': "Comment 1"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.engagement_rate, 1)
        self.assertEqual(self.post.comments.count(), 1)
        created_comment = Comment.objects.latest("id")
        self.assertEqual(created_comment.post, self.post)
        self.assertEqual(created_comment.text, "Comment 1")
        self.assertEqual(created_comment.user.id, MyUser.objects.latest("id").id)
        self.assertTrue(created_comment.time + datetime.timedelta(seconds=3) > timezone.now())
        self.assertTrue(created_comment.time < timezone.now())

    def test_valid_data_plus_extra_data(self):
        """
        Testing the behavior in case of some additional data like time being sent.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user2}')
        self.assertEqual(self.post.engagement_rate, 0)
        url = reverse('api_posts-add_comment', args=[Post.objects.latest('id').id])
        data = {
            "text": "Comment 1",
            "time": datetime.datetime(year=2222, month=7, day=4),
            "id": 10000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.engagement_rate, 1)
        self.assertEqual(self.post.comments.count(), 1)
        created_comment = Comment.objects.latest("id")
        self.assertEqual(created_comment.post, self.post)
        self.assertEqual(created_comment.text, "Comment 1")
        self.assertEqual(created_comment.user.id, MyUser.objects.latest("id").id)
        self.assertTrue(created_comment.time + datetime.timedelta(seconds=3) > timezone.now())
        self.assertTrue(created_comment.time < timezone.now())
        last_id = Comment.objects.latest("id").id
        self.assertEqual(response.data, {"text": "Comment 1", "id": last_id})
        self.assertNotEqual(response.data, {"text": "Comment 1", "id": 10000})

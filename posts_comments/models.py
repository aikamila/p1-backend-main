from django.db import models
from django.conf import settings


class CommonInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=5000)
    time = models.DateTimeField(verbose_name="Time of posting")

    class Meta:
        abstract = True


class Post(CommonInfo):
    engagement_rate = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-time']
#         ordering of models works in serializers too


class Comment(CommonInfo):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        ordering = ['time']


class Reply(CommonInfo):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")

    class Meta:
        ordering = ['time']




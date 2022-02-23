from django.db.models.signals import post_save
from .models import Comment, Reply


def grow_engagement_comment(sender, instance, created, **kwargs):
    """
    Function responsible for increasing engagement rate under a post
    if a new comment is created by user other than the author
    """
    if created and instance.user != instance.post.user:
        post = instance.post
        post.engagement_rate += 1
        post.save()


post_save.connect(grow_engagement_comment, sender=Comment)


def grow_engagement_reply(sender, instance, created, **kwargs):
    """
    Function responsible for increasing engagement rate under a post
    if a new reply is created by user other than the author
    """
    if created and instance.user != instance.comment.post.user:
        post = instance.comment.post
        post.engagement_rate += 1
        post.save()


post_save.connect(grow_engagement_reply, sender=Reply)

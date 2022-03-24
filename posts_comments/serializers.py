from rest_framework import serializers
from .models import Post, Comment, Reply
from user.serializers import BasicInfoUserSerializer
from django.utils import timezone


def calculate_time_since_posted(created, current):
    """
    Function that calculates time passed between two datetime objects, approximates it
    and returns a string in a human-readable form
    """
    time_delta = current - created
    if time_delta.days // 365:
        if time_delta.days // 365 > 1:
            return str(time_delta.days // 365) + ' years ago'
        else:
            return '1 year ago'
    if time_delta.days // 30:
        if time_delta.days // 30 > 1:
            return str(time_delta.days // 30) + ' months ago'
        else:
            return '1 month ago'
    if time_delta.days > 0:
        if time_delta.days > 1:
            return str(time_delta.days) + ' days ago'
        else:
            return '1 day ago'
    if time_delta.seconds // 3600:
        if time_delta.seconds // 3600 > 1:
            return str(time_delta.seconds // 3600) + ' hours ago'
        else:
            return '1 hour ago'
    if time_delta.seconds // 60:
        if time_delta.seconds // 60 > 1:
            return str(time_delta.seconds // 60) + ' minutes ago'
        else:
            return '1 minute ago'
    return 'Just now'


class PostListSerializer(serializers.ModelSerializer):
    user = BasicInfoUserSerializer()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'user', 'time_since_posted', 'engagement_rate']

    def get_time_since_posted(self, obj):
        return calculate_time_since_posted(obj.time, timezone.now())


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text']

    def validate_text(self, value):
        if len(value.strip()) <= 30:
            raise serializers.ValidationError("Post must contain at least 30 characters")
        return value

    def create(self, validated_data):
        user = self.context['user']
        return Post.objects.create(user=user, time=timezone.now(), **validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class ReplyListSerializer(serializers.ModelSerializer):
    user = BasicInfoUserSerializer()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'user', 'text', 'time_since_posted']

    def get_time_since_posted(self, obj):
        return calculate_time_since_posted(obj.time, timezone.now())


class CommentListSerializer(serializers.ModelSerializer):
    user = BasicInfoUserSerializer()
    replies = ReplyListSerializer(many=True)
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'time_since_posted', "replies"]

    def get_time_since_posted(self, obj):
        return calculate_time_since_posted(obj.time, timezone.now())


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'id']
        extra_kwargs = {"id": {'read_only': True}}

    def create(self, validated_data):
        user = self.context['user']
        post = self.context['post']
        return Comment.objects.create(user=user, post=post, time=timezone.now(), **validated_data)


class PostRetrieveSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True)
    user = BasicInfoUserSerializer()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'text', 'time_since_posted', 'comments']

    def get_time_since_posted(self, obj):
        return calculate_time_since_posted(obj.time, timezone.now())


class ReplyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['text', 'id']
        extra_kwargs = {"id": {'read_only': True}}

    def create(self, validated_data):
        user = self.context['user']
        comment = self.context['comment']
        return Reply.objects.create(user=user, comment=comment, time=timezone.now(), **validated_data)


class BasicInfoPostSerializer(serializers.ModelSerializer):
    time_since_posted = serializers.SerializerMethodField()
    user = BasicInfoUserSerializer()

    class Meta:
        model = Post
        fields = ['id', 'user', 'text', 'time_since_posted']

    def get_time_since_posted(self, obj):
        return calculate_time_since_posted(obj.time, timezone.now())

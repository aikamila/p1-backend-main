from rest_framework import serializers
from .models import Post, Comment, Reply, CommonInfo
from user.serializers import UserSerializer, BasicInfoUserSerializer
from django.utils import timezone


class TimeSincePostedCalculator:
    """
    Class that calculates time passed between two datetime objects, approximates it
    and returns a string in a human-readable form
    """
    def __init__(self, created, current):
        self._time_delta = current - created

    def _calculate(self):
        if self._time_delta.days // 365:
            if self._time_delta.days // 365 > 1:
                return str(self._time_delta.days // 365) + ' years ago'
            else:
                return '1 year ago'
        if self._time_delta.days // 30:
            if self._time_delta.days // 30 > 1:
                return str(self._time_delta.days // 30) + ' months ago'
            else:
                return '1 month ago'
        if self._time_delta.days > 0:
            if self._time_delta.days > 1:
                return str(self._time_delta.days) + ' days ago'
            else:
                return '1 day ago'
        if self._time_delta.seconds // 3600:
            if self._time_delta.seconds // 3600 > 1:
                return str(self._time_delta.seconds // 3600) + ' hours ago'
            else:
                return '1 hour ago'
        if self._time_delta.seconds // 60:
            if self._time_delta.seconds // 60 > 1:
                return str(self._time_delta.seconds // 60) + ' minutes ago'
            else:
                return '1 minute ago'
        return 'Just now'

    def calculate_string(self):
        return self._calculate()


class PostListSerializer(serializers.ModelSerializer):
    user = BasicInfoUserSerializer()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'user', 'time_since_posted', 'engagement_rate']

    def get_time_since_posted(self, obj):
        return TimeSincePostedCalculator(obj.time, timezone.now()).calculate_string()


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
        return TimeSincePostedCalculator(obj.time, timezone.now()).calculate_string()


class CommentListSerializer(serializers.ModelSerializer):
    user = BasicInfoUserSerializer()
    replies = ReplyListSerializer(many=True)
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'time_since_posted', "replies"]

    def get_time_since_posted(self, obj):
        return TimeSincePostedCalculator(obj.time, timezone.now()).calculate_string()


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'id']
        extra_kwargs = {"id": {'read_only': True}}
    #
    # def validate_text(self, value):
    #     if len(value.strip()) == 0:
    #         raise serializers.ValidationError
    #     return value

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
        return TimeSincePostedCalculator(obj.time, timezone.now()).calculate_string()


class ReplyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['text', 'id']
        extra_kwargs = {"id": {'read_only': True}}

    # def validate_text(self, value):
    #     if len(value.strip()) == 0:
    #         raise serializers.ValidationError
    #     return value

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
        return TimeSincePostedCalculator(obj.time, timezone.now()).calculate_string()

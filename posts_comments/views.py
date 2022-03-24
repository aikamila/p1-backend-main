from rest_framework import viewsets, status
from .serializers import PostListSerializer, PostCreateUpdateSerializer, PostRetrieveSerializer, \
    CommentCreateUpdateSerializer, ReplyCreateUpdateSerializer, BasicInfoPostSerializer
from .models import Post, Comment, Reply
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__id']

    def list(self, request, *args, **kwargs):
        """
        Listing all posts or listing filtered posts
        """
        queryset = self.filter_queryset(Post.objects.select_related('user'))
        serializer = PostListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Retrieving all information about a post, optimising performance of the db
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': "This post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        post = Post.objects.select_related('user').\
            prefetch_related(Prefetch('comments', queryset=Comment.objects.select_related('user').
                                      prefetch_related(Prefetch('replies', queryset=Reply.objects.select_related('user')))))\
            .get(pk=pk)
        serializer = PostRetrieveSerializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], url_path="comments/add", url_name="add_comment")
    def add_comment(self, request, pk=None):
        """
        Adding a comment below a specific post
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': "This post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        serializer = CommentCreateUpdateSerializer(data=request.data, context={'user': user, 'post': post})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Creating a new post
        """
        user = request.user
        serializer = PostCreateUpdateSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Updating a specific post
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': "This post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user.id != post.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PostCreateUpdateSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Deleting a specific post
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': "This post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user.id != post.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'], url_path="basic", url_name="basic_info")
    def retrieve_basic_info(self, request, pk=None):
        """
        Retrieving basic information about a post - without
        the information about comments and replies
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': "This post doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BasicInfoPostSerializer(post)
        return Response(serializer.data)


class CommentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'], url_path="replies/add", url_name="add_reply")
    def add_reply(self, request, pk=None):
        """
        Adding a reply under a specific comment
        """
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'message': "This comment doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        serializer = ReplyCreateUpdateSerializer(data=request.data, context={'user': user, 'comment': comment})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

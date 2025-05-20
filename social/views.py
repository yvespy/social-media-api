from django.db.models import Prefetch
from rest_framework import viewsets

from social.models import Post, Comment
from social.serializers import (
    PostSerializer,
    CommentSerializer,
    PostListSerializer,
    CommentListSerializer,
    PostDetailSerializer,
    CommentDetailSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_queryset(self):
        return Post.objects.select_related("author").prefetch_related(
            "likes",
            Prefetch(
                "comments", queryset=Comment.objects.select_related("author", "post")
            ),
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_queryset(self):
        return Comment.objects.select_related("author", "post")

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        elif self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

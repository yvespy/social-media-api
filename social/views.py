from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from social.models import Post, Comment
from social.permissions import IsAuthorOrReadOnly
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = [filters.SearchFilter]
    search_fields = ["title"]

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

    @extend_schema(
        summary="List posts",
        description="Retrieve list of posts, optionally filtered by title.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search posts by title.",
                required=False,
                type=str,
            )
        ],
        responses=PostListSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a post",
        description="Retrieve detailed information about a single post including its comments.",
        responses=PostDetailSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a post",
        description="Create a new post. User must be authenticated.",
        request=PostSerializer,
        responses=PostSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update a post",
        description="Update a post. Only the author can update their post.",
        request=PostSerializer,
        responses=PostSerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update a post",
        description="Partially update a post. Only the author can update their post.",
        request=PostSerializer,
        responses=PostSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a post",
        description="Delete a post. Only the author can delete their post.",
        responses={204: OpenApiResponse(description="Post deleted")},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

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

    @extend_schema(
        summary="List comments",
        description="Retrieve list of comments.",
        responses=CommentListSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a comment",
        description="Retrieve detailed information about a single comment.",
        responses=CommentDetailSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a comment",
        description="Create a new comment on a post. User must be authenticated.",
        request=CommentSerializer,
        responses=CommentSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update a comment",
        description="Update a comment. Only the author can update their comment.",
        request=CommentSerializer,
        responses=CommentSerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update a comment",
        description="Partially update a comment. Only the author can update their comment.",
        request=CommentSerializer,
        responses=CommentSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a comment",
        description="Delete a comment. Only the author can delete their comment.",
        responses={204: OpenApiResponse(description="Comment deleted")},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

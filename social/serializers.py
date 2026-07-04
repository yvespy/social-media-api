from rest_framework import serializers

from social.models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "author", "likes", "created_at")
        read_only_fields = ("author", "created_at")


class PostListSerializer(PostSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    comments = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta(PostSerializer.Meta):
        fields = ("id", "title", "author_username", "likes", "created_at", "comments")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "created_at")
        read_only_fields = ("author", "created_at")


class CommentListSerializer(CommentSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta(CommentSerializer.Meta):
        fields = ("id", "post_title", "author_username", "content", "created_at")


class CommentDetailSerializer(CommentListSerializer):
    post_content = serializers.CharField(source="post.content", read_only=True)

    class Meta(CommentListSerializer.Meta):
        fields = CommentListSerializer.Meta.fields + ("post_content",)


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    users_liked = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = (
            "id",
            "title",
            "content",
            "author_username",
            "users_liked",
            "created_at",
            "comments",
        )

    def get_users_liked(self, obj):
        return [user.username for user in obj.likes.all()]

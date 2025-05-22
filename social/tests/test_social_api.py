import json
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from users.models import User
from social.models import Post, Comment


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SocialTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass1234")
        self.other_user = User.objects.create_user(
            username="user2", password="pass1234"
        )

        self.post = Post.objects.create(
            title="Test Post", content="Some content", author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post, content="Test comment", author=self.user
        )

        self.post_list_url = reverse("post-list")
        self.post_detail_url = reverse("post-detail", kwargs={"pk": self.post.id})
        self.comment_list_url = reverse("comment-list")
        self.comment_detail_url = reverse(
            "comment-detail", kwargs={"pk": self.comment.id}
        )

        self.tokens_user = get_tokens_for_user(self.user)
        self.tokens_other_user = get_tokens_for_user(self.other_user)

    def authenticate(self, user_tokens):
        self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {user_tokens['access']}"

    def test_post_list(self):
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("title", response.json()[0])

    def test_post_create_requires_authentication(self):
        data = {"title": "New Post", "content": "Post content"}
        response = self.client.post(self.post_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_success(self):
        self.authenticate(self.tokens_user)
        data = {"title": "New Post", "content": "Post content"}
        response = self.client.post(
            self.post_list_url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_update_by_author(self):
        self.authenticate(self.tokens_user)
        response = self.client.patch(
            self.post_detail_url,
            data=json.dumps({"content": "Updated"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Updated")

    def test_post_update_by_non_author(self):
        self.authenticate(self.tokens_other_user)
        response = self.client.patch(
            self.post_detail_url,
            data=json.dumps({"content": "Hacked"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_list(self):
        response = self.client.get(self.comment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_comment_create_authenticated(self):
        self.authenticate(self.tokens_user)
        data = {"post": self.post.id, "content": "Another comment"}
        response = self.client.post(
            self.comment_list_url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_comment_update_by_non_author(self):
        self.authenticate(self.tokens_other_user)
        response = self.client.patch(
            self.comment_detail_url,
            data=json.dumps({"content": "nope"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from social.models import Post, Comment


class SocialAPITestCase(APITestCase):
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

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_post_list(self):
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("title", response.data[0])

    def test_post_create_requires_authentication(self):
        data = {"title": "New Post", "content": "Post content"}
        response = self.client.post(self.post_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_success(self):
        self.authenticate(self.user)
        data = {"title": "New Post", "content": "Post content"}
        response = self.client.post(self.post_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_update_by_author(self):
        self.authenticate(self.user)
        response = self.client.patch(self.post_detail_url, {"content": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Updated")

    def test_post_update_by_non_author(self):
        self.authenticate(self.other_user)
        response = self.client.patch(self.post_detail_url, {"content": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_list(self):
        response = self.client.get(self.comment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_comment_create_authenticated(self):
        self.authenticate(self.user)
        data = {"post": self.post.id, "content": "Another comment"}
        response = self.client.post(self.comment_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_comment_update_by_non_author(self):
        self.authenticate(self.other_user)
        response = self.client.patch(self.comment_detail_url, {"content": "nope"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

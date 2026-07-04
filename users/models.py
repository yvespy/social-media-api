from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(max_length=255, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures", blank=True, null=True
    )


class UserFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following_user"], name="unique_following"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} is following {self.following_user}"

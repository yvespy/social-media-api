from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(max_length=255, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures", blank=True, null=True
    )

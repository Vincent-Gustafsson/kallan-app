from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


def user_avatar_upload_to(instance: "User", filename: str) -> str:
    return f"users/{instance.pk or 'new'}/avatar/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    class Tier(models.TextChoices):
        BANDANA = "bandana", "Bandana"
        HAT = "hat", "Hat"
        VEST = "vest", "Vest"

    username = models.CharField(max_length=150, unique=True)

    tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        default=Tier.VEST,
    )

    avatar = models.ImageField(
        upload_to=user_avatar_upload_to,
        blank=True,
        null=True,
    )

    force_password_reset = models.BooleanField(default=True)

    # Required admin-related fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self) -> str:
        return self.username

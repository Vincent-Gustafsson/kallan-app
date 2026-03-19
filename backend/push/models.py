from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class WebPushSubscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )

    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)

    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    def as_webpush_dict(self):
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


class NotificationPreferences(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_prefs",
    )

    # Fine-grained per-type toggles (all enabled by default)
    punishment_proposed = models.BooleanField(default=True)
    punishment_confirmed = models.BooleanField(default=True)
    punishment_cancelled = models.BooleanField(default=True)
    punishment_taken = models.BooleanField(default=True)
    fikapinne_given = models.BooleanField(default=True)
    fikapinne_taken = models.BooleanField(default=True)

    @classmethod
    def for_user(cls, user) -> "NotificationPreferences":
        prefs, _ = cls.objects.get_or_create(user=user)
        return prefs

    def is_enabled(self, notification_type: str) -> bool:
        return bool(getattr(self, notification_type, True))

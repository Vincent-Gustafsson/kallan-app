import json

from django.conf import settings
from pywebpush import WebPushException, webpush

from .models import NotificationPreferences, WebPushSubscription


def send_push_to_user(user, payload: dict, notification_type: str | None = None) -> int:
    # Check per-type preference before doing any work
    if notification_type is not None:
        prefs = NotificationPreferences.for_user(user)
        if not prefs.is_enabled(notification_type):
            return 0

    ok = 0
    subs = WebPushSubscription.objects.filter(user=user)

    for sub in subs:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
            ok += 1
        except WebPushException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (404, 410):
                sub.delete()
            else:
                print("PUSH Failed")
                print(e)

    return ok


def send_push_to_users(
    users, payload: dict, notification_type: str | None = None
) -> int:
    """Send a push notification to multiple users, respecting per-user preferences.

    More efficient than calling send_push_to_user in a loop when sending to many users,
    because it batches the subscription query and preference checks.
    """

    user_ids = [u.pk for u in users]

    # Load all prefs for these users in one query (only if we care about type)
    disabled_ids: set[int] = set()
    if notification_type is not None:
        from django.db.models import Q

        prefs_qs = NotificationPreferences.objects.filter(user_id__in=user_ids)
        for prefs in prefs_qs:
            if not prefs.is_enabled(notification_type):
                disabled_ids.add(prefs.user_id)

    # Load all subscriptions for eligible users in one query
    eligible_ids = [uid for uid in user_ids if uid not in disabled_ids]
    subs = WebPushSubscription.objects.filter(user_id__in=eligible_ids)

    ok = 0
    for sub in subs:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
            ok += 1
        except WebPushException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (404, 410):
                sub.delete()
            else:
                print("PUSH Failed")
                print(e)

    return ok

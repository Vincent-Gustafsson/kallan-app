import json

from django.conf import settings
from pywebpush import WebPushException, webpush

from .models import WebPushSubscription


def send_push_to_user(user, payload: dict) -> int:
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
                print("PUSH Faiiled")
                print(e)

    return ok

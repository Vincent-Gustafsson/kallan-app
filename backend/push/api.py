from django.conf import settings
from django.utils import timezone
from ninja import Schema
from ninja.router import Router

from .models import WebPushSubscription

router = Router(tags=["push"])


class SubscriptionKeys(Schema):
    p256dh: str
    auth: str


class SubscriptionIn(Schema):
    endpoint: str
    keys: SubscriptionKeys


@router.get("/vapid-public-key")
def vapid_public_key(request):
    return {"publicKey": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe")
def subscribe(request, payload: SubscriptionIn):
    user = request.user
    WebPushSubscription.objects.update_or_create(
        endpoint=payload.endpoint,
        defaults={
            "user": user,
            "p256dh": payload.keys.p256dh,
            "auth": payload.keys.auth,
            "last_seen_at": timezone.now(),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )
    return {"ok": True}


@router.post("/unsubscribe")
def unsubscribe(request, payload: SubscriptionIn):
    WebPushSubscription.objects.filter(
        endpoint=payload.endpoint, user=request.user
    ).delete()
    return {"ok": True}

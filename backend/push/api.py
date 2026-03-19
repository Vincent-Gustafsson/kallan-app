from django.conf import settings
from django.utils import timezone
from ninja import Schema
from ninja.router import Router

from .models import NotificationPreferences, WebPushSubscription

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


class UnsubscribeIn(Schema):
    endpoint: str


@router.post("/unsubscribe")
def unsubscribe(request, payload: UnsubscribeIn):
    WebPushSubscription.objects.filter(
        endpoint=payload.endpoint, user=request.user
    ).delete()
    return {"ok": True}


class NotificationPrefsOut(Schema):
    punishment_proposed: bool
    punishment_confirmed: bool
    punishment_cancelled: bool
    punishment_taken: bool
    fikapinne_given: bool
    fikapinne_taken: bool


class NotificationPrefsIn(Schema):
    punishment_proposed: bool
    punishment_confirmed: bool
    punishment_cancelled: bool
    punishment_taken: bool
    fikapinne_given: bool
    fikapinne_taken: bool


@router.get("/notification-prefs", response=NotificationPrefsOut)
def get_notification_prefs(request):
    prefs = NotificationPreferences.for_user(request.user)
    return prefs


@router.put("/notification-prefs", response=NotificationPrefsOut)
def update_notification_prefs(request, payload: NotificationPrefsIn):
    prefs = NotificationPreferences.for_user(request.user)
    for field in NotificationPrefsIn.model_fields:
        setattr(prefs, field, getattr(payload, field))
    prefs.save()
    return prefs

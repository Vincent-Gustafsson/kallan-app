from datetime import datetime, timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError
from push.tasks import send_push_to_user_task, send_push_to_users_task
from .tasks import expire_punishment_event
from pydantic import Field

from .models import (
    FikapinneEvent,
    PunishmentEvent,
    TakeFikapinneEvent,
    TakePunishmentEvent,
)

User = get_user_model()
router = Router(tags=["punishments"])


class UserMiniOut(Schema):
    id: int
    username: str
    avatar_url: Optional[str] = None
    tier: str


class PunishmentEventOut(Schema):
    id: int
    target: UserMiniOut
    initiator: UserMiniOut
    confirmer: Optional[UserMiniOut]

    reason: str
    amount: int

    created_at: datetime
    confirmed_at: Optional[datetime]
    stage: str  # "pending"


class CreatePunishmentEventIn(Schema):
    target_id: int
    amount: int = Field(ge=1, le=10)
    reason: str = Field("", max_length=50)


class PunishmentStatsOut(Schema):
    target_id: int
    total_amount: int
    week_amount: int


class TakePunishmentIn(Schema):
    target_id: int
    amount: int = Field(ge=1, le=10)


class TakePunishmentOut(Schema):
    id: int
    target: UserMiniOut
    judge: UserMiniOut
    amount: int
    created_at: datetime


def _user_mini(u: Optional[User]) -> Optional[dict]:
    if u is None:
        return None

    avatar_url = None
    avatar = getattr(u, "avatar", None)
    try:
        if avatar:
            avatar_url = avatar.url
    except Exception:
        avatar_url = None

    return {
        "id": u.id,
        "username": getattr(u, "username", None) or u.get_username(),
        "avatar_url": avatar_url,
        "tier": getattr(u, "tier", None) or "bandana",
    }


def _event_out(e: PunishmentEvent) -> dict:
    return {
        "id": e.id,
        "target": _user_mini(e.target),
        "initiator": _user_mini(e.initiator),
        "confirmer": _user_mini(e.confirmer),
        "reason": e.reason or "",
        "amount": e.amount,
        "created_at": e.created_at,
        "confirmed_at": e.confirmed_at,
        "stage": e.stage,
    }


def _take_out(t: TakePunishmentEvent) -> dict:
    return {
        "id": t.id,
        "target": _user_mini(t.target),
        "judge": _user_mini(t.judge),
        "amount": t.amount,
        "created_at": t.created_at,
    }


@router.post("/events", response={201: PunishmentEventOut})
def create_event(request, payload: CreatePunishmentEventIn):
    initiator = request.user

    if payload.target_id == initiator.id:
        raise HttpError(400, "You cannot punish yourself.")

    initiator_tier = getattr(initiator, "tier", None) or "bandana"
    if initiator_tier == "bandana":
        raise HttpError(403, "Bandanas cannot give punishments.")

    target = get_object_or_404(User, pk=payload.target_id)

    is_direct = initiator.has_perm("punishments.direct_punish")

    try:
        e = PunishmentEvent.objects.create(
            target=target,
            initiator=initiator,
            reason=payload.reason or "",
            amount=payload.amount,
            is_direct=is_direct,
            confirmed_at=timezone.now() if is_direct else None,
        )
    except IntegrityError:
        raise HttpError(400, "Invalid punishment (constraint violation).")

    initiator_username = initiator.username
    target_username = target.username
    amount = e.amount
    reason = (e.reason or "").strip()

    others_ids = list(
        User.objects.filter(is_active=True)
        .exclude(Q(id=initiator.id) | Q(id=target.id))
        .values_list("id", flat=True)
    )
    _target_id = target.id
    _event_id = e.id

    # pre-compute everything needed for notifications before on_commit
    if is_direct:
        body_t = f"Antal: {amount}"
        if reason:
            body_t += f" Anledning: {reason}"
        payload_target = {"title": "Bongsköterskan gav dig straff!", "body": body_t, "url": "/punishments"}

        body_o = f"Bongsköterskan gav {target_username} +{amount} straff."
        if reason:
            body_o += f" Anledning: {reason}"
        payload_others = {"title": "Bongsköterskan gav straff", "body": body_o, "url": "/punishments"}

        def _schedule():
            send_push_to_user_task.delay(_target_id, payload_target, "punishment_confirmed")
            send_push_to_users_task.delay(others_ids, payload_others, "punishment_confirmed")
    else:
        body_t = f"Antal: {amount}"
        if reason:
            body_t += f" Anledning: {reason}"
        payload_target = {"title": f"{initiator_username} vill ge dig straff!", "body": body_t, "url": "/punishments"}

        body_o = f"{initiator_username} vill ge {target_username} +{amount} straff."
        if reason:
            body_o += f" Anledning: {reason}"
        payload_others = {"title": "Nytt straff-förslag", "body": body_o, "url": "/punishments"}

        def _schedule():
            send_push_to_user_task.delay(_target_id, payload_target, "punishment_proposed")
            send_push_to_users_task.delay(others_ids, payload_others, "punishment_proposed")
            expire_punishment_event.apply_async(args=[_event_id], countdown=300)

    transaction.on_commit(_schedule)

    e = PunishmentEvent.objects.select_related("target", "initiator", "confirmer").get(
        pk=e.pk
    )

    return 201, _event_out(e)


@router.get("/events", response=list[PunishmentEventOut])
def list_events(
    request,
    pending: int = 0,
    confirmed: int = 0,
    limit: int | None = None,
    target_id: int | None = None,
):
    qs = PunishmentEvent.objects.select_related(
        "target", "initiator", "confirmer"
    ).order_by("-created_at")

    if target_id is not None:
        qs = qs.filter(target_id=target_id)

    if pending == 1 and confirmed == 1:
        if limit is not None:
            qs = qs[:limit]
        return [_event_out(e) for e in qs]

    if pending == 1:
        qs = qs.pending()
        if limit is not None:
            qs = qs[:limit]
        return [_event_out(e) for e in qs]

    if confirmed == 1:
        qs = qs.delivered()
        if limit is not None:
            qs = qs[:limit]

        return [_event_out(e) for e in qs]

    raise HttpError(400, "Set pending=1 or confirmed=1 (or both).")


@router.post("/events/{event_id}/confirm", response={200: PunishmentEventOut})
def confirm_event(request, event_id: int):
    confirmer = request.user

    confirmer_tier = getattr(confirmer, "tier", None)
    if confirmer_tier is None:
        raise HttpError(400, "User tier is missing.")
    if confirmer_tier == "bandana":
        raise HttpError(403, "Bandanas cannot confirm punishments.")

    with transaction.atomic():
        # IMPORTANT: lock ONLY the PunishmentEvent row (no outer joins)
        e = (
            PunishmentEvent.objects.select_for_update()
            .select_related(
                "target", "initiator"
            )  # confirmer is nullable -> avoid here
            .filter(pk=event_id)
            .first()
        )
        if not e:
            raise HttpError(404, "Punishment event not found.")

        if e.confirmer_id is not None:
            raise HttpError(400, "This punishment is already confirmed.")

        if e.target_id == confirmer.id:
            raise HttpError(403, "Target cannot confirm their own punishment.")
        if e.initiator_id == confirmer.id:
            raise HttpError(403, "Initiator cannot confirm their own punishment.")

        initiator_tier = getattr(e.initiator, "tier", None)
        if initiator_tier is None:
            raise HttpError(400, "Initiator tier is missing.")
        if initiator_tier == "bandana":
            raise HttpError(403, "Bandanas cannot participate in confirmations.")

        # Allowed: vest+vest or hat+vest (either order)
        allowed = (initiator_tier == "vest" and confirmer_tier in ("hat", "vest")) or (
            confirmer_tier == "vest" and initiator_tier in ("hat", "vest")
        )
        if not allowed:
            raise HttpError(403, "Not allowed to confirm (tier rule).")

        e.confirmer = confirmer
        e.confirmed_at = timezone.now()
        e.save(update_fields=["confirmer", "confirmed_at"])

        # capture values for the closure (safe after commit)
        target = e.target
        initiator = e.initiator
        amount = e.amount
        reason = (e.reason or "").strip()
        confirmer_username = confirmer.username
        target_username = target.username

        body_t = f"{confirmer_username} bekräftade straffet (+{amount})."
        if reason:
            body_t += f" Anledning: {reason}"
        _payload_target = {"title": "Straff bekräftat", "body": body_t, "url": "/punishments"}

        body_i = f"{confirmer_username} bekräftade straffet mot {target_username} (+{amount})."
        if reason:
            body_i += f" Anledning: {reason}"
        _payload_initiator = {"title": "Ditt straff blev bekräftat", "body": body_i, "url": "/punishments"}

        _target_id = target.id
        _initiator_id = initiator.id

        def _schedule():
            send_push_to_user_task.delay(_target_id, _payload_target, "punishment_confirmed")
            send_push_to_user_task.delay(_initiator_id, _payload_initiator, "punishment_confirmed")

        transaction.on_commit(_schedule)

    # fetch full output (including confirmer) AFTER the transaction
    e = PunishmentEvent.objects.select_related("target", "initiator", "confirmer").get(
        pk=event_id
    )
    return 200, _event_out(e)


@router.delete("/events/{event_id}", response={204: None})
def delete_event(request, event_id: int):
    me = request.user

    with transaction.atomic():
        e = (
            PunishmentEvent.objects.select_for_update()
            .select_related("target", "initiator")  # both non-null, safe
            .filter(pk=event_id)
            .first()
        )
        if not e:
            raise HttpError(404, "Punishment event not found.")

        # Only pending can be deleted
        if e.confirmer_id is not None:
            raise HttpError(400, "Cannot delete a confirmed punishment.")

        # Only initiator can delete
        if e.initiator_id != me.id:
            raise HttpError(403, "Only the initiator can delete this punishment.")

        # capture data BEFORE delete for notification
        target = e.target
        initiator_username = e.initiator.username
        amount = e.amount
        reason = (e.reason or "").strip()

        e.delete()

        body = f"{initiator_username} ångrade straffet (+{amount})."
        if reason:
            body += f" Anledning: {reason}"
        _payload = {"title": "Straff ångrat", "body": body, "url": "/punishments"}
        _target_id = target.id

        transaction.on_commit(
            lambda: send_push_to_user_task.delay(_target_id, _payload, "punishment_cancelled")
        )

    return 204, None


@router.get("/stats", response=PunishmentStatsOut)
def punishment_stats(request, target_id: int | None = None):
    if target_id is None:
        if not request.user or not request.user.is_authenticated:
            raise HttpError(401, "Not authenticated.")
        target_id = request.user.id

    tz = timezone.get_current_timezone()
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())  # Monday
    next_week_start = week_start + timedelta(days=7)

    week_start_dt = timezone.make_aware(
        datetime.combine(week_start, datetime.min.time()), tz
    )
    next_week_start_dt = timezone.make_aware(
        datetime.combine(next_week_start, datetime.min.time()), tz
    )

    delivered = PunishmentEvent.objects.delivered().filter(
        target_id=target_id,
    )

    delivered_total = delivered.aggregate(s=Sum("amount"))["s"] or 0
    delivered_week = (
        delivered.filter(
            confirmed_at__gte=week_start_dt,
            confirmed_at__lt=next_week_start_dt,
        ).aggregate(s=Sum("amount"))["s"]
        or 0
    )

    taken = TakePunishmentEvent.objects.filter(target_id=target_id)

    taken_total = taken.aggregate(s=Sum("amount"))["s"] or 0

    total_amount = max(0, int(delivered_total) - int(taken_total))

    return {
        "target_id": target_id,
        "total_amount": total_amount,
        "week_amount": int(delivered_week),
    }


@router.post("/take", response={201: TakePunishmentOut})
def take_punishment(request, payload: TakePunishmentIn):
    judge = request.user

    judge_tier = getattr(judge, "tier", None) or "bandana"
    if judge_tier != "vest":
        raise HttpError(403, "Only vests can take punishments.")

    if payload.target_id == judge.id:
        raise HttpError(400, "Judge cannot take punishments from themselves.")

    with transaction.atomic():
        target = get_object_or_404(
            User.objects.select_for_update(), pk=payload.target_id
        )

        delivered_total = (
            PunishmentEvent.objects.delivered().filter(
                target=target
            ).aggregate(s=Sum("amount"))["s"]
            or 0
        )

        taken_total = (
            TakePunishmentEvent.objects.filter(target=target).aggregate(
                s=Sum("amount")
            )["s"]
            or 0
        )

        available = int(delivered_total) - int(taken_total)
        if payload.amount > available:
            raise HttpError(
                400, f"Inte tillräckligt många straff kvar, antal kvar: {available}"
            )

        t = TakePunishmentEvent.objects.create(
            target=target,
            judge=judge,
            amount=payload.amount,
        )

        judge_username = judge.username
        amount = t.amount

        _payload = {
            "title": "Straff strukna",
            "body": f"{judge_username} strök {amount} straff från dig.",
            "url": "/",
        }
        _target_id = target.id

        transaction.on_commit(
            lambda: send_push_to_user_task.delay(_target_id, _payload, "punishment_taken")
        )

    t = TakePunishmentEvent.objects.select_related("target", "judge").get(pk=t.pk)
    return 201, _take_out(t)


class GiveFikapinneIn(Schema):
    target_id: int


class TakeFikapinneIn(Schema):
    target_id: int
    amount: int


def _require_manage_fikapinnar(request) -> User:
    u = getattr(request, "auth", None) or getattr(request, "user", None)
    if not u or not getattr(u, "is_authenticated", False):
        raise HttpError(401, "Not authenticated.")
    if not u.has_perm("punishments.manage_fikapinnar"):
        raise HttpError(403, "Not allowed.")
    return u


@router.post("/fikapinnar/give")
def give_fikapinne(request, payload: GiveFikapinneIn):
    judge = _require_manage_fikapinnar(request)

    if payload.target_id == judge.id:
        raise HttpError(400, "You cannot give yourself a fikapinne.")

    target = get_object_or_404(User, pk=payload.target_id)

    FikapinneEvent.objects.create(
        target=target,
        judge=judge,
    )

    judge_username = judge.username

    _target_id = target.id
    _payload = {
        "title": "Du fick en fikapinne ☕️",
        "body": f"{judge_username} gav dig en fikapinne.",
        "url": "/",
    }

    transaction.on_commit(
        lambda: send_push_to_user_task.delay(_target_id, _payload, "fikapinne_given")
    )

    return HttpResponse(status=201)


@router.post("/fikapinnar/take")
def take_fikapinnar(request, payload: TakeFikapinneIn):
    judge = _require_manage_fikapinnar(request)

    if payload.target_id == judge.id:
        raise HttpError(400, "You cannot take from yourself.")

    if payload.amount not in (3, 5):
        raise HttpError(400, "Amount must be 3 or 5.")

    target = get_object_or_404(User, pk=payload.target_id)

    given_total = FikapinneEvent.objects.filter(target=target).count()
    taken_total = (
        TakeFikapinneEvent.objects.filter(target=target).aggregate(s=Sum("amount"))["s"]
        or 0
    )
    current_total = max(0, int(given_total) - int(taken_total))

    if payload.amount > current_total:
        raise HttpError(400, f"Inte tillräckligt många fikapinnar ({current_total})")

    TakeFikapinneEvent.objects.create(
        target=target,
        judge=judge,
        amount=payload.amount,
    )

    judge_username = judge.username

    _target_id = target.id
    _fikapinne_amount = payload.amount
    _payload = {
        "title": "Fikapinnar borttagna",
        "body": f"{judge_username} tog bort {_fikapinne_amount} fikapinnar.",
        "url": "/",
    }

    transaction.on_commit(
        lambda: send_push_to_user_task.delay(_target_id, _payload, "fikapinne_taken")
    )

    return HttpResponse(status=201)


class FikapinneStatsOut(Schema):
    target_id: int
    total_amount: int
    month_amount: int


@router.get("/fikapinnar/stats", response=FikapinneStatsOut)
def fikapinne_stats(request, target_id: int | None = None):
    if target_id is None:
        if not request.user or not request.user.is_authenticated:
            raise HttpError(401, "Not authenticated.")
        target_id = request.user.id

    tz = timezone.get_current_timezone()
    today = timezone.localdate()

    # month boundaries: first day of this month -> first day of next month
    month_start = today.replace(day=1)
    if month_start.month == 12:
        next_month_start = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month_start = month_start.replace(month=month_start.month + 1)

    month_start_dt = timezone.make_aware(
        datetime.combine(month_start, datetime.min.time()), tz
    )
    next_month_start_dt = timezone.make_aware(
        datetime.combine(next_month_start, datetime.min.time()), tz
    )

    given = FikapinneEvent.objects.filter(target_id=target_id)
    taken = TakeFikapinneEvent.objects.filter(target_id=target_id)

    given_total = given.count()
    taken_total = taken.aggregate(s=Sum("amount"))["s"] or 0

    # month_amount = given this month only (no subtract)
    month_amount = given.filter(
        created_at__gte=month_start_dt,
        created_at__lt=next_month_start_dt,
    ).count()

    total_amount = max(0, int(given_total) - int(taken_total))

    return {
        "target_id": target_id,
        "total_amount": total_amount,
        "month_amount": int(month_amount),
    }

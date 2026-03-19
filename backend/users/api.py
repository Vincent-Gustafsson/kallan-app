from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from ninja import File, Router, Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.security import SessionAuth

from django.db.models import Count, Sum

from punishments.models import FikapinneEvent, PunishmentEvent, TakeFikapinneEvent, TakePunishmentEvent
from users.schemas import MeOut, UserMiniOut, UserWithStatsOut
from users.utils import user_to_mini

User = get_user_model()

router = Router(tags=["users"])
session_auth = SessionAuth()


@router.post("/csrf", auth=None)
@ensure_csrf_cookie
@csrf_exempt
def csrf(request):
    # sets csrftoken cookie
    return HttpResponse(status=204)


class LoginIn(Schema):
    username: str
    password: str


@router.post("/login", auth=None)
def login(request, payload: LoginIn):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        raise HttpError(401, "Fel källannamn eller lösenord")
    if not user.is_active:
        raise HttpError(403, "User is inactive")

    django_login(request, user)
    return {"ok": True, "force_password_reset": user.force_password_reset}


@router.post("/logout", auth=None)
def logout(request):
    django_logout(request)
    return {"ok": True}


class SetPasswordIn(Schema):
    new_password: str


@router.post("/set-password", auth=session_auth)
def set_password(request, payload: SetPasswordIn):
    user = request.auth
    user.set_password(payload.new_password)
    user.force_password_reset = False
    user.save(update_fields=["password", "force_password_reset"])
    update_session_auth_hash(request, user)
    return {"ok": True}


@router.get("/me", auth=session_auth, response=MeOut)
def me(request):
    u = request.auth
    data = user_to_mini(request, u)
    data["force_password_reset"] = u.force_password_reset
    return data


@router.post("/me/avatar", response=MeOut)
def set_avatar(request, avatar: UploadedFile = File(...)):
    user = request.auth

    if avatar.content_type and not avatar.content_type.startswith("image/"):
        raise HttpError(400, "Profilbild måste vara en bild")

    max_bytes = 5 * 1024 * 1024
    if avatar.size and avatar.size > max_bytes:
        raise HttpError(400, "Profilbild för stor (max 5MB)")

    old_name = user.avatar.name if user.avatar else None

    user.avatar = avatar
    user.save(update_fields=["avatar"])

    # Delete old file to avoid orphaned uploads
    if old_name and old_name != user.avatar.name:
        try:
            user.avatar.storage.delete(old_name)
        except Exception:
            pass

    data = user_to_mini(request, user)
    data["force_password_reset"] = user.force_password_reset
    return data


@router.get("", response=list[UserWithStatsOut])
def list_users(
    request,
    q: str | None = None,
    exclude_me: bool = True,
    limit: int = 50,
):
    me = request.auth

    if limit < 1 or limit > 50:
        raise HttpError(400, "INVALID_LIMIT")

    qs = User.objects.all()

    if exclude_me and me and getattr(me, "is_authenticated", False):
        qs = qs.exclude(id=me.id)

    if q:
        q = q.strip()
        if q:
            qs = qs.filter(username__icontains=q)

    users_list = list(qs.order_by("username")[:limit])
    if not users_list:
        return []

    user_ids = [u.id for u in users_list]

    delivered = dict(
        PunishmentEvent.objects.filter(target_id__in=user_ids, confirmer__isnull=False)
        .values("target_id")
        .annotate(total=Sum("amount"))
        .values_list("target_id", "total")
    )
    taken_punishments = dict(
        TakePunishmentEvent.objects.filter(target_id__in=user_ids)
        .values("target_id")
        .annotate(total=Sum("amount"))
        .values_list("target_id", "total")
    )
    given_fika = dict(
        FikapinneEvent.objects.filter(target_id__in=user_ids)
        .values("target_id")
        .annotate(total=Count("id"))
        .values_list("target_id", "total")
    )
    taken_fika = dict(
        TakeFikapinneEvent.objects.filter(target_id__in=user_ids)
        .values("target_id")
        .annotate(total=Sum("amount"))
        .values_list("target_id", "total")
    )

    results = []
    for u in users_list:
        data = user_to_mini(request, u)
        d = int(delivered.get(u.id, 0) or 0)
        t = int(taken_punishments.get(u.id, 0) or 0)
        data["punishment_count"] = max(0, d - t)
        gf = int(given_fika.get(u.id, 0) or 0)
        tf = int(taken_fika.get(u.id, 0) or 0)
        data["fikapinne_count"] = max(0, gf - tf)
        results.append(data)
    return results


@router.get("/{user_id}", response=UserMiniOut)
def get_user(request, user_id: int):
    u = get_object_or_404(User, id=user_id)
    return user_to_mini(request, u)

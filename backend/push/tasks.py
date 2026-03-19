from celery import shared_task


@shared_task
def send_push_to_user_task(user_id: int, payload: dict, notification_type: str | None = None) -> int:
    from django.contrib.auth import get_user_model
    from .services import send_push_to_user

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return 0
    return send_push_to_user(user, payload, notification_type)


@shared_task
def send_push_to_users_task(user_ids: list[int], payload: dict, notification_type: str | None = None) -> int:
    from django.contrib.auth import get_user_model
    from .services import send_push_to_users

    if not user_ids:
        return 0

    User = get_user_model()
    users = list(User.objects.filter(pk__in=user_ids))
    return send_push_to_users(users, payload, notification_type)

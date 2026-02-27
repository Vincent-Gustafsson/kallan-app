from .schemas import UserMiniOut


def user_to_mini(request, user) -> dict:
    avatar_url = (
        request.build_absolute_uri(user.avatar.url)
        if getattr(user, "avatar", None)
        else None
    )
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": avatar_url,
        "tier": user.tier,
        "permissions": list(user.get_all_permissions()),
    }

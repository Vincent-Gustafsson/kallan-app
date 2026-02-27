from ninja import NinjaAPI
from ninja.errors import AuthorizationError
from ninja.security import SessionAuth
from punishments.api import router as punishments_router
from push.api import router as push_router
from users.api import router as users_router


class SessionAuthNoForcedReset(SessionAuth):
    def authenticate(self, request, token=None):
        user = request.user
        if not user or not user.is_authenticated:
            return None
        if getattr(user, "force_password_reset", False):
            raise AuthorizationError(message="PASSWORD_RESET_REQUIRED")
        return user


api = NinjaAPI(auth=SessionAuthNoForcedReset())
api.add_router("/users/", users_router)
api.add_router("/punishments/", punishments_router)
api.add_router("/push/", push_router)

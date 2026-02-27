from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Profile"), {"fields": ("tier", "avatar", "force_password_reset")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "avatar",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "tier",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "force_password_reset",
        "tier",
    )
    search_fields = ("username",)
    ordering = ("-tier",)

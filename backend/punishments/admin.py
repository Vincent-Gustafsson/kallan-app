from django.contrib import admin
from django.utils.html import format_html

from .models import (
    FikapinneEvent,
    PunishmentEvent,
    TakeFikapinneEvent,
    TakePunishmentEvent,
)

admin.site.register(TakePunishmentEvent)
admin.site.register(FikapinneEvent)
admin.site.register(TakeFikapinneEvent)


@admin.register(PunishmentEvent)
class PunishmentEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stage",
        "initiator",
        "confirmer",
        "target",
        "amount",
        "short_reason",
        "created_at",
        "confirmed_at",
    )
    list_filter = ("confirmer", "created_at", "confirmed_at")
    search_fields = (
        "target__username",
        "initiator__username",
        "confirmer__username",
        "reason",
    )
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "confirmed_at", "stage")
    autocomplete_fields = ("target", "initiator", "confirmer")

    fieldsets = (
        (None, {"fields": ("target", "initiator", "confirmer")}),
        ("Punishment", {"fields": ("reason", "amount")}),
        ("Status", {"fields": ("stage", "created_at", "confirmed_at")}),
    )

    @admin.display(description="Stage")
    def stage(self, obj: PunishmentEvent):
        return "pending" if obj.confirmer_id is None else "delivered"

    @admin.display(description="Reason")
    def short_reason(self, obj: PunishmentEvent):
        s = obj.reason.strip()
        return s if len(s) <= 50 else s[:47] + "..."

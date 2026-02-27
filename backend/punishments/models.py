from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F, Q, Sum
from django.utils import timezone

User = get_user_model()


class PunishmentEventQuerySet(models.QuerySet):
    def delivered(self):
        return self.filter(confirmer__isnull=False)

    def pending(self):
        return self.filter(confirmer__isnull=True)

    def for_target(self, user):
        return self.filter(target=user)

    def involving(self, user):
        return self.filter(Q(target=user) | Q(initiator=user) | Q(confirmer=user))

    def total_delivered_for(self, user) -> int:
        return self.delivered().for_target(user).aggregate(s=Sum("amount"))["s"] or 0


class PunishmentEvent(models.Model):
    target = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="punishment_events_received"
    )
    initiator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="punishment_events_initiated"
    )
    confirmer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="punishment_events_confirmed",
        null=True,
        blank=True,
    )

    reason = models.TextField(blank=True, default="")
    amount = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    objects = PunishmentEventQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(initiator=F("target")), name="pe_initiator_not_target"
            ),
            models.CheckConstraint(
                condition=Q(confirmer__isnull=True) | ~Q(confirmer=F("initiator")),
                name="pe_confirmer_not_initiator",
            ),
            models.CheckConstraint(
                condition=Q(confirmer__isnull=True) | ~Q(confirmer=F("target")),
                name="pe_confirmer_not_target",
            ),
        ]

    @property
    def stage(self) -> str:
        return "pending" if self.confirmer_id is None else "confirmed"

    def confirm(self, user):
        if user.pk in {self.initiator_id, self.target_id}:
            raise ValueError("Confirmer must be a different user.")

        # race-safe confirm (optional but nice)
        with transaction.atomic():
            updated = PunishmentEvent.objects.filter(
                pk=self.pk, confirmer__isnull=True
            ).update(confirmer=user, confirmed_at=timezone.now())
            if updated == 0:
                raise ValueError("Already confirmed.")
            self.confirmer_id = user.pk
            self.confirmed_at = timezone.now()


class TakePunishmentEvent(models.Model):
    target = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="punishment_takes_received"
    )
    judge = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="punishment_takes_judged"
    )

    amount = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(judge=F("target")),
                name="pte_judge_not_target",
            ),
        ]


class FikapinneEvent(models.Model):
    target = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fikapinnar_received"
    )
    judge = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="fikapinnar_given"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("manage_fikapinnar", "Can give/take fikapinnar"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(judge=F("target")),
                name="fe_judge_not_target",
            ),
        ]


class TakeFikapinneEvent(models.Model):
    target = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fikapinnar_taken_from"
    )
    judge = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="fikapinnar_taken_by"
    )

    amount = models.PositiveSmallIntegerField()  # API enforces 3 or 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(judge=F("target")),
                name="tfe_judge_not_target",
            ),
        ]

    def __str__(self) -> str:
        return f"TakeFikapinne({self.target_id}, -{self.amount})"

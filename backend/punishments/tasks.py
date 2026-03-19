from celery import shared_task


@shared_task
def expire_punishment_event(event_id: int) -> None:
    """Delete a pending punishment event if it still hasn't been confirmed."""
    from .models import PunishmentEvent

    PunishmentEvent.objects.filter(pk=event_id, confirmer__isnull=True).delete()

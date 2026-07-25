from __future__ import annotations

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Item
from .services import send_user_notification


@receiver(pre_save, sender=Item)
def capture_previous_owner(
    sender: type[Item],
    instance: Item,
    **kwargs,
) -> None:
    if not instance.pk:
        instance._previous_owner_id = None
        return

    previous_owner_id = (
        sender.objects
        .filter(pk=instance.pk)
        .values_list("owner_id", flat=True)
        .first()
    )

    instance._previous_owner_id = previous_owner_id


@receiver(post_save, sender=Item)
def notify_item_changed(
    sender: type[Item],
    instance: Item,
    created: bool,
    **kwargs,
) -> None:
    if created:
        return

    previous_owner_id = getattr(
        instance,
        "_previous_owner_id",
        None,
    )

    current_owner_id = instance.owner_id

    if previous_owner_id != current_owner_id:
        if previous_owner_id is not None:
            send_user_notification(
                user_id=previous_owner_id,
                event_type="item.owner_changed",
                message=(
                    f'Запись «{instance.name}» больше вам не принадлежит.'
                ),
                item_id=instance.pk,
            )

        if current_owner_id is not None:
            send_user_notification(
                user_id=current_owner_id,
                event_type="item.assigned",
                message=(
                    f'Вам назначена запись «{instance.name}».'
                ),
                item_id=instance.pk,
            )

        return

    if current_owner_id is not None:
        send_user_notification(
            user_id=current_owner_id,
            event_type="item.updated",
            message=(
                f'Запись «{instance.name}» была изменена.'
            ),
            item_id=instance.pk,
        )

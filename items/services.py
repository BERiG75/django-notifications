from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction


def get_user_group_name(user_id: int) -> str:
    return f"user_{user_id}"


def _send_user_notification(
    *,
    user_id: int,
    event_type: str,
    message: str,
    item_id: int,
) -> None:
    channel_layer = get_channel_layer()

    if channel_layer is None:
        return

    group_name = get_user_group_name(user_id)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notification.message",
            "event_type": event_type,
            "message": message,
            "item_id": item_id,
        },
    )


def send_user_notification(
    *,
    user_id: int,
    event_type: str,
    message: str,
    item_id: int,
) -> None:
    transaction.on_commit(
        lambda: _send_user_notification(
            user_id=user_id,
            event_type=event_type,
            message=message,
            item_id=item_id,
        )
    )

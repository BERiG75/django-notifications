from __future__ import annotations

from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .services import get_user_group_name


class ItemNotificationConsumer(AsyncJsonWebsocketConsumer):
    group_name: str

    async def connect(self) -> None:
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close(code=4401)
            return

        self.group_name = get_user_group_name(user.id)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def notification_message(
        self,
        event: dict[str, Any],
    ) -> None:
        await self.send_json(
            {
                "event_type": event["event_type"],
                "message": event["message"],
                "item_id": event["item_id"],
            }
        )

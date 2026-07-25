from django.urls import path

from .consumers import ItemNotificationConsumer

websocket_urlpatterns = [
    path(
        "ws/notifications/",
        ItemNotificationConsumer.as_asgi(),
    ),
]

from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "name",
    )

    list_select_related = (
        "owner",
    )

    ordering = (
        "-created_at",
        "-id",
    )

    list_per_page = 50
    
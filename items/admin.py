from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .filters import NameFilter, UsernameFilter
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

    list_filter = (
        "owner",
        "name",
        UsernameFilter,
        NameFilter,
    )
    
    ordering = (
        "-created_at",
        "-id",
    )

    list_per_page = 50

    def get_queryset(self, request: HttpRequest) -> QuerySet[Item]:
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            return queryset

        return queryset.filter(owner=request.user)

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Item | None = None,
    ) -> tuple[str, ...]:
        if request.user.is_superuser:
            return ()

        return ("owner",)


    def save_model(
        self,
        request: HttpRequest,
        obj: Item,
        form,
        change: bool,
    ) -> None:
        if not change and not request.user.is_superuser:
            obj.owner = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )

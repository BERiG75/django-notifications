import csv

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import path

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

    change_list_template = (
        "admin/items/item/change_list.html"
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

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "export-csv/",
                self.admin_site.admin_view(self.export_csv),
                name="items_item_export_csv",
            ),
        ]

        return custom_urls + urls

    def export_csv(self, request: HttpRequest) -> HttpResponse:
        if not request.user.has_perm("items.export_items_csv"):
            raise PermissionDenied

        queryset = (
            self.get_queryset(request)
            .select_related("owner")
        )

        response = HttpResponse(
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = (
            'attachment; filename="items.csv"'
        )

        response.write("\ufeff")

        writer = csv.writer(
            response,
            delimiter=";",
            lineterminator="\r\n",
        )

        writer.writerow(
            [
                "id",
                "name",
                "description",
                "username",
                "created_at",
                "updated_at",
            ]
        )

        for item in queryset.iterator():
            writer.writerow(
                [
                    item.pk,
                    item.name,
                    item.description,
                    item.owner.username,
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                ]
            )

        return response

    # def has_export_csv_permission(
    #     self,
    #     request: HttpRequest,
    # ) -> bool:
    #     opts = self.model._meta
    #     codename = get_permission_codename(
    #         "export_items_csv",
    #         opts,
    #     )

    #     return request.user.has_perm(
    #         f"{opts.app_label}.{codename}"
    #     )

    # def changelist_view(
    #     self,
    #     request: HttpRequest,
    #     extra_context=None,
    # ):
    #     if extra_context is None:
    #         extra_context = {}

    #     extra_context["has_export_csv_permission"] = (
    #         self.has_export_csv_permission(request)
    #     )

    #     return super().changelist_view(
    #         request,
    #         extra_context=extra_context,
    #     )

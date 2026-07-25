from __future__ import annotations

from typing import Any
from django.http import HttpRequest
from django.contrib import admin
from django.db.models import QuerySet


class TextInputFilter(admin.SimpleListFilter):
    template = "admin/filters/text_filter.html"

    lookup: str = "icontains"

    def has_output(self) -> bool:
        return True

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin,
    ) -> tuple[tuple[str, str], ...]:
        return ()

    def queryset(
        self,
        request: Any,
        queryset: QuerySet,
    ) -> QuerySet:
        value = self.value()

        if not value:
            return queryset

        return queryset.filter(
            **{f"{self.field_name}__{self.lookup}": value}
        )


class UsernameFilter(TextInputFilter):
    title = "Username"
    parameter_name = "username"
    field_name: str = "owner__username"


class NameFilter(TextInputFilter):
    title = "Name"
    parameter_name = "name_contains"
    field_name: str = "name"
    
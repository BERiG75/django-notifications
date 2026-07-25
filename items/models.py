from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Item(models.Model):
    name = models.CharField(
        verbose_name="Name",
        max_length=255,
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
    )
    owner = models.ForeignKey(
        User,
        verbose_name="Owner",
        on_delete=models.CASCADE,
        related_name="items",
    )
    created_at = models.DateTimeField(
        verbose_name="Created at",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Updated at",
        auto_now=True,
    )

    class Meta:
        db_table = "items"
        ordering = ("id",)
        permissions = (
            (
                "export_items_csv",
                "Can export items to CSV",
            ),
        )
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self) -> str:
        return self.name

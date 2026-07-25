from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from items.models import Item


User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users and items for local Docker environment."

    SUPERUSER_USERNAME = "admin"
    SUPERUSER_EMAIL = "admin@example.com"
    SUPERUSER_PASSWORD = "password"

    USER_ONE_USERNAME = "ivan"
    USER_ONE_EMAIL = "ivan@example.com"
    USER_ONE_PASSWORD = "ivanivan"

    USER_TWO_USERNAME = "petr"
    USER_TWO_EMAIL = "petr@example.com"
    USER_TWO_PASSWORD = "petrpetr"

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._get_or_create_superuser()

        user_one = self._get_or_create_user(
            username=self.USER_ONE_USERNAME,
            email=self.USER_ONE_EMAIL,
            password=self.USER_ONE_PASSWORD,
        )

        user_two = self._get_or_create_user(
            username=self.USER_TWO_USERNAME,
            email=self.USER_TWO_EMAIL,
            password=self.USER_TWO_PASSWORD,
        )

        self._grant_item_permissions(
            user_one,
            include_export=True,
        )

        self._grant_item_permissions(
            user_two,
            include_export=False,
        )

        self._create_items(
            owner=user_one,
            prefix="Ivan item",
            count=5,
        )

        self._create_items(
            owner=user_two,
            prefix="Petr item",
            count=5,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data has been created successfully."
            )
        )

        self.stdout.write(
            f"Superuser: {admin.username}"
        )

        self.stdout.write(
            f"Staff user 1: {user_one.username}"
        )

        self.stdout.write(
            f"Staff user 2: {user_two.username}"
        )

    def _get_or_create_superuser(self):
        user, created = User.objects.get_or_create(
            username=self.SUPERUSER_USERNAME,
            defaults={
                "email": self.SUPERUSER_EMAIL,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False

        if not user.is_staff:
            user.is_staff = True
            changed = True

        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        if user.email != self.SUPERUSER_EMAIL:
            user.email = self.SUPERUSER_EMAIL
            changed = True

        user.set_password(self.SUPERUSER_PASSWORD)

        if changed:
            user.save(
                update_fields=[
                    "email",
                    "is_staff",
                    "is_superuser",
                    "password",
                ]
            )
        else:
            user.save(update_fields=["password"])

        return user

    def _get_or_create_user(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
            },
        )

        changed = False

        if user.email != email:
            user.email = email
            changed = True

        if not user.is_staff:
            user.is_staff = True
            changed = True

        if user.is_superuser:
            user.is_superuser = False
            changed = True

        user.set_password(password)

        if changed:
            user.save(
                update_fields=[
                    "email",
                    "is_staff",
                    "is_superuser",
                    "password",
                ]
            )
        else:
            user.save(
                update_fields=[
                    "password",
                ]
            )

        return user

    def _grant_item_permissions(
        self,
        user,
        *,
        include_export: bool,
    ) -> None:
        permissions = Permission.objects.filter(
            content_type__app_label=Item._meta.app_label,
            content_type__model=Item._meta.model_name,
        )

        if not include_export:
            permissions = permissions.exclude(
                codename="export_items_csv",
            )

        user.user_permissions.set(permissions)

    def _create_items(
        self,
        *,
        owner,
        prefix: str,
        count: int,
    ):
        for index in range(1, count + 1):
            Item.objects.get_or_create(
                name=f"{prefix} {index}",
                defaults={
                    "description": (
                        f"Demo description for {prefix} {index}"
                    ),
                    "owner": owner,
                },
            )
            
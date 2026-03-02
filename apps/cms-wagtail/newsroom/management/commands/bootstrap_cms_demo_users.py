from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


ROLES = [
    "reporter",
    "desk",
    "editor_in_chief",
    "ops_admin",
    "portal_admin",
]


class Command(BaseCommand):
    help = "Create demo CMS users for each role group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="ChangeMe123!",
            help="Password to set for all demo users.",
        )

    def handle(self, *args, **options):
        password = options["password"]
        user_model = get_user_model()

        missing_groups = [role for role in ROLES if not Group.objects.filter(name=role).exists()]
        if missing_groups:
            raise CommandError(
                "Missing role groups: {}. Run `python manage.py bootstrap_cms_rbac` first.".format(
                    ", ".join(missing_groups)
                )
            )

        for role in ROLES:
            username = f"demo_{role}"
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@local.test",
                    "is_staff": True,
                    "is_active": True,
                },
            )
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=["is_staff"])

            user.set_password(password)
            user.save(update_fields=["password"])

            group = Group.objects.get(name=role)
            user.groups.clear()
            user.groups.add(group)

            label = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f"{label}: {username} ({role})"))

        self.stdout.write(
            self.style.WARNING(
                "Demo user password set. Rotate or remove these accounts outside local testing."
            )
        )

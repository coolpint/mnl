from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Ensure a reporter-level CMS user exists and is assigned to reporter group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.getenv("CMS_REPORTER_USERNAME", "").strip(),
            help="Reporter username (default: CMS_REPORTER_USERNAME).",
        )
        parser.add_argument(
            "--email",
            default=os.getenv("CMS_REPORTER_EMAIL", "").strip(),
            help="Reporter email (default: CMS_REPORTER_EMAIL).",
        )
        parser.add_argument(
            "--password",
            default=os.getenv("CMS_REPORTER_PASSWORD", ""),
            help="Reporter password (default: CMS_REPORTER_PASSWORD).",
        )
        parser.add_argument(
            "--skip-if-missing",
            action="store_true",
            help="Skip without error when username/password is missing.",
        )

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        email = (options.get("email") or "").strip()
        password = options.get("password") or ""
        skip_if_missing = bool(options.get("skip_if_missing"))

        missing = []
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")

        if missing:
            message = (
                "Missing reporter credentials ({fields}). Set CMS_REPORTER_USERNAME/CMS_REPORTER_PASSWORD "
                "or pass --username/--password."
            ).format(fields=", ".join(missing))
            if skip_if_missing:
                self.stdout.write(self.style.WARNING(f"Skip reporter bootstrap: {message}"))
                return
            raise CommandError(message)

        reporter_group = Group.objects.filter(name="reporter").first()
        if reporter_group is None:
            raise CommandError("Missing role group 'reporter'. Run `python manage.py bootstrap_cms_rbac` first.")

        user_model = get_user_model()
        fallback_email = f"{username}@local.test"
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email or fallback_email,
                "is_staff": True,
                "is_active": True,
            },
        )

        update_fields: list[str] = []
        if user.email != (email or user.email):
            user.email = email or user.email
            update_fields.append("email")
        elif not user.email:
            user.email = fallback_email
            update_fields.append("email")

        if not user.is_staff:
            user.is_staff = True
            update_fields.append("is_staff")
        if not user.is_active:
            user.is_active = True
            update_fields.append("is_active")

        if getattr(user, "is_superuser", False):
            user.is_superuser = False
            update_fields.append("is_superuser")

        if update_fields:
            user.save(update_fields=update_fields)

        user.set_password(password)
        user.save(update_fields=["password"])

        user.groups.set([reporter_group])

        label = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{label}: reporter user '{username}' assigned to reporter group with staff access"
            )
        )

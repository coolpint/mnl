from __future__ import annotations

from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase


class BootstrapReporterUserCommandTests(TestCase):
    def setUp(self) -> None:
        Group.objects.create(name="reporter")
        Group.objects.create(name="desk")
        self.user_model = get_user_model()

    def test_creates_reporter_user_with_expected_access(self):
        call_command(
            "bootstrap_cms_reporter_user",
            "--username",
            "reporter_account",
            "--email",
            "reporter@example.com",
            "--password",
            "StrongPass!123",
        )

        user = self.user_model.objects.get(username="reporter_account")
        self.assertEqual(user.email, "reporter@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(getattr(user, "is_superuser", False))
        self.assertEqual(list(user.groups.values_list("name", flat=True)), ["reporter"])
        self.assertTrue(user.check_password("StrongPass!123"))

    def test_updates_existing_user_to_reporter_only(self):
        user = self.user_model.objects.create_user(
            username="existing_editor",
            password="oldpass",
            email="existing@example.com",
            is_staff=False,
            is_active=False,
            is_superuser=True,
        )
        user.groups.add(Group.objects.get(name="desk"))

        call_command(
            "bootstrap_cms_reporter_user",
            "--username",
            "existing_editor",
            "--password",
            "NewPass!123",
        )

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertEqual(list(user.groups.values_list("name", flat=True)), ["reporter"])
        self.assertTrue(user.check_password("NewPass!123"))

    def test_skip_if_missing_does_not_fail(self):
        stdout = StringIO()
        call_command("bootstrap_cms_reporter_user", "--skip-if-missing", stdout=stdout)
        output = stdout.getvalue()
        self.assertIn("Skip reporter bootstrap", output)

from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from newsroom.models import ArticleAuditLog, ArticlePage


GROUP_PERMISSIONS = {
    "reporter": {
        "access_admin",
        "add_articlepage",
        "change_articlepage",
        "view_articlepage",
        "submit_desk_review",
    },
    "desk": {
        "access_admin",
        "change_articlepage",
        "view_articlepage",
        "approve_article",
        "schedule_article",
        "retract_article",
        "apply_l2_update",
        "submit_desk_review",
        "publish_page",
    },
    "editor_in_chief": {
        "access_admin",
        "add_articlepage",
        "change_articlepage",
        "view_articlepage",
        "delete_articlepage",
        "approve_article",
        "schedule_article",
        "retract_article",
        "archive_article",
        "apply_l2_update",
        "create_l3_followup",
        "submit_desk_review",
        "publish_page",
    },
    "ops_admin": {
        "access_admin",
        "view_articlepage",
        "view_articleauditlog",
    },
    "portal_admin": {
        "access_admin",
        "view_articlepage",
        "view_articleauditlog",
    },
}

PERMISSION_TARGETS = {
    "add_articlepage": ("newsroom", "articlepage"),
    "change_articlepage": ("newsroom", "articlepage"),
    "delete_articlepage": ("newsroom", "articlepage"),
    "view_articlepage": ("newsroom", "articlepage"),
    "submit_desk_review": ("newsroom", "articlepage"),
    "approve_article": ("newsroom", "articlepage"),
    "schedule_article": ("newsroom", "articlepage"),
    "retract_article": ("newsroom", "articlepage"),
    "archive_article": ("newsroom", "articlepage"),
    "apply_l2_update": ("newsroom", "articlepage"),
    "create_l3_followup": ("newsroom", "articlepage"),
    "view_articleauditlog": ("newsroom", "articleauditlog"),
    "access_admin": ("wagtailadmin", "admin"),
    "publish_page": ("wagtailcore", "page"),
}


class Command(BaseCommand):
    help = "Create CMS RBAC groups and bind model permissions."

    def handle(self, *args, **options):
        # Ensure content types are available before assigning permissions.
        ContentType.objects.get_for_model(ArticlePage)
        ContentType.objects.get_for_model(ArticleAuditLog)

        for group_name, codename_set in GROUP_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()

            assigned = 0
            missing: list[str] = []
            for codename in sorted(codename_set):
                target = PERMISSION_TARGETS.get(codename)
                if target is None:
                    missing.append(codename)
                    continue
                app_label, model = target
                content_type = ContentType.objects.filter(
                    app_label=app_label,
                    model=model,
                ).first()
                if content_type is None:
                    missing.append(codename)
                    continue
                permission = Permission.objects.filter(
                    content_type=content_type,
                    codename=codename,
                ).first()
                if permission is None:
                    missing.append(codename)
                    continue
                group.permissions.add(permission)
                assigned += 1

            self.stdout.write(
                self.style.SUCCESS(f"[{group_name}] assigned {assigned} permissions")
            )
            if missing:
                self.stdout.write(
                    self.style.WARNING(
                        f"[{group_name}] missing permissions: {', '.join(missing)}"
                    )
                )

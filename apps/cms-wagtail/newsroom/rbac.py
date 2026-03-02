from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser


REPORTER = "reporter"
DESK = "desk"
EDITOR_IN_CHIEF = "editor_in_chief"
OPS_ADMIN = "ops_admin"
PORTAL_ADMIN = "portal_admin"

EDITORIAL_ROLES = (REPORTER, DESK, EDITOR_IN_CHIEF, OPS_ADMIN, PORTAL_ADMIN)

ROLE_PRIORITY = (
    EDITOR_IN_CHIEF,
    DESK,
    REPORTER,
    OPS_ADMIN,
    PORTAL_ADMIN,
)


def resolve_user_role(user: AbstractBaseUser) -> str:
    if not getattr(user, "is_authenticated", False):
        return REPORTER

    if getattr(user, "is_superuser", False):
        return EDITOR_IN_CHIEF

    group_names = set(user.groups.values_list("name", flat=True))
    for role in ROLE_PRIORITY:
        if role in group_names:
            return role
    return REPORTER

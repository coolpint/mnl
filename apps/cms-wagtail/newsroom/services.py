from __future__ import annotations

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ArticleAuditLog, ArticlePage, ArticleStatus
from .rbac import DESK, EDITOR_IN_CHIEF, OPS_ADMIN, PORTAL_ADMIN, REPORTER, resolve_user_role


SEOUL_TZ = ZoneInfo("Asia/Seoul")

TRANSITION_MAP: dict[str, set[str]] = {
    ArticleStatus.DRAFT: {ArticleStatus.WRITING},
    ArticleStatus.WRITING: {ArticleStatus.DESK_REVIEW},
    ArticleStatus.DESK_REVIEW: {
        ArticleStatus.DESK_REWORK,
        ArticleStatus.APPROVED,
        ArticleStatus.SCHEDULED,
    },
    ArticleStatus.DESK_REWORK: {ArticleStatus.WRITING, ArticleStatus.DESK_REVIEW},
    ArticleStatus.APPROVED: {ArticleStatus.PUBLISHED},
    ArticleStatus.SCHEDULED: {ArticleStatus.PUBLISHED, ArticleStatus.DESK_REVIEW},
    ArticleStatus.PUBLISHED: {
        ArticleStatus.PUBLISHED_UPDATED,
        ArticleStatus.RETRACTED,
        ArticleStatus.ARCHIVED,
    },
    ArticleStatus.PUBLISHED_UPDATED: {
        ArticleStatus.RETRACTED,
        ArticleStatus.ARCHIVED,
    },
    ArticleStatus.RETRACTED: {ArticleStatus.ARCHIVED},
    ArticleStatus.ARCHIVED: set(),
}

ROLE_TARGETS: dict[str, set[str]] = {
    REPORTER: {ArticleStatus.WRITING, ArticleStatus.DESK_REVIEW},
    DESK: {
        ArticleStatus.DESK_REWORK,
        ArticleStatus.APPROVED,
        ArticleStatus.SCHEDULED,
        ArticleStatus.PUBLISHED,
        ArticleStatus.PUBLISHED_UPDATED,
        ArticleStatus.RETRACTED,
    },
    EDITOR_IN_CHIEF: set(TRANSITION_MAP.keys()),
    OPS_ADMIN: set(),
    PORTAL_ADMIN: set(),
}


def available_targets(current_status: str, role: str) -> list[str]:
    next_states = TRANSITION_MAP.get(current_status, set())
    allowed_targets = ROLE_TARGETS.get(role, set())
    return sorted(next_states & allowed_targets)


def parse_scheduled_at_from_kst(raw_value: str) -> datetime:
    if not raw_value:
        raise ValidationError("Scheduled datetime is required.")

    parsed = datetime.fromisoformat(raw_value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SEOUL_TZ)
    return parsed.astimezone(timezone.utc)


@transaction.atomic
def apply_transition(
    *,
    article: ArticlePage,
    target_status: str,
    actor: AbstractBaseUser,
    scheduled_at: Optional[datetime] = None,
    note: str = "",
) -> None:
    role = resolve_user_role(actor)
    current = article.workflow_status

    allowed_by_graph = target_status in TRANSITION_MAP.get(current, set())
    if not allowed_by_graph:
        raise ValidationError(f"Invalid status transition: {current} -> {target_status}")

    if target_status not in ROLE_TARGETS.get(role, set()):
        raise PermissionDenied(f"Role '{role}' cannot move article to {target_status}")

    if target_status == ArticleStatus.SCHEDULED:
        if scheduled_at is None:
            raise ValidationError("scheduled_at is required for scheduled transition.")
        if scheduled_at <= timezone.now():
            raise ValidationError("Scheduled time must be in the future.")
        article.scheduled_publish_at = scheduled_at
        article.go_live_at = scheduled_at
    else:
        article.scheduled_publish_at = None
        if target_status != ArticleStatus.PUBLISHED:
            article.go_live_at = None

    article.workflow_status = target_status
    article.full_clean()
    article.save()

    if target_status in {ArticleStatus.PUBLISHED, ArticleStatus.PUBLISHED_UPDATED}:
        article.published_revision_no += 1
        article.save(update_fields=["published_revision_no"])
        article.save_revision(user=actor).publish()

    if target_status in {ArticleStatus.RETRACTED, ArticleStatus.ARCHIVED} and article.live:
        article.unpublish()

    ArticleAuditLog.objects.create(
        article=article,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action="status_transition",
        from_status=current,
        to_status=target_status,
        details={
            "role": role,
            "scheduled_at": scheduled_at.isoformat() if scheduled_at else "",
            "note": note.strip(),
        },
    )

from __future__ import annotations

from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from .models import ArticleAuditLog, ArticlePage, ArticleStatus
from .rbac import resolve_user_role
from .services import apply_transition, available_targets, parse_scheduled_at_from_kst


def _require_staff(request: HttpRequest) -> Optional[HttpResponse]:
    if not request.user.is_staff:
        return HttpResponseForbidden("Staff access required.")
    return None


@login_required
def desk_queue_view(request: HttpRequest) -> HttpResponse:
    forbidden = _require_staff(request)
    if forbidden is not None:
        return forbidden

    role = resolve_user_role(request.user)
    articles = ArticlePage.objects.select_related("reporter", "desk_editor").order_by(
        "-latest_revision_created_at"
    )[:200]

    rows: list[dict[str, object]] = []
    for article in articles:
        targets = available_targets(article.workflow_status, role)
        action_buttons = [
            {
                "value": target,
                "label": ArticleStatus(target).label,
                "requires_schedule": target == ArticleStatus.SCHEDULED,
            }
            for target in targets
        ]
        rows.append({"article": article, "targets": action_buttons})

    context = {
        "rows": rows,
        "role": role,
        "audit_logs": ArticleAuditLog.objects.select_related("actor", "article")[:30],
    }
    return TemplateResponse(request, "newsroom/admin/desk_queue.html", context)


@login_required
def transition_article_view(request: HttpRequest, page_id: int) -> HttpResponse:
    forbidden = _require_staff(request)
    if forbidden is not None:
        return forbidden

    if request.method != "POST":
        return redirect("newsroom_desk_queue")

    article = get_object_or_404(ArticlePage, pk=page_id)
    target_status = request.POST.get("target_status", "").strip()
    note = request.POST.get("note", "").strip()
    scheduled_raw = request.POST.get("scheduled_at", "").strip()

    scheduled_at = None
    if target_status == ArticleStatus.SCHEDULED:
        try:
            scheduled_at = parse_scheduled_at_from_kst(scheduled_raw)
        except Exception as exc:
            messages.error(request, f"예약 시간 파싱 실패: {exc}")
            return redirect("newsroom_desk_queue")

    try:
        apply_transition(
            article=article,
            target_status=target_status,
            actor=request.user,
            scheduled_at=scheduled_at,
            note=note,
        )
    except Exception as exc:
        messages.error(request, f"전이 실패: {exc}")
    else:
        messages.success(
            request,
            f"{article.article_id} 상태가 {target_status}로 변경되었습니다.",
        )
    return redirect("newsroom_desk_queue")

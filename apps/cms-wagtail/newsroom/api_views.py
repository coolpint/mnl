from __future__ import annotations

import json
import os
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils.html import escape, strip_tags
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import ArticleAuditLog, ArticlePage, ArticleStatus, NewsroomHomePage, Section


PUBLISHED_STATES = (ArticleStatus.PUBLISHED, ArticleStatus.PUBLISHED_UPDATED)
AI_ALLOWED_INTENTS = (ArticleStatus.WRITING, ArticleStatus.DESK_REVIEW)


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _body_text(article: ArticlePage) -> str:
    return _normalize_text(strip_tags(article.body or ""))


def _summary(article: ArticlePage) -> str:
    source = article.search_description or _body_text(article)
    source = _normalize_text(source)
    return source[:220]


def _to_payload(article: ArticlePage) -> dict[str, Any]:
    reporter = article.reporter
    reporter_id = reporter.username if reporter else "desk"
    reporter_name = (
        reporter.get_full_name().strip() if reporter and reporter.get_full_name().strip() else reporter_id
    )

    published_at = article.first_published_at or article.last_published_at
    updated_at = article.latest_revision_created_at or article.last_published_at or article.first_published_at

    body_text = _body_text(article)
    paragraphs = [segment.strip() for segment in body_text.split(". ") if segment.strip()]

    return {
        "id": article.article_id,
        "slug": article.slug,
        "headline": article.title,
        "subheadline": article.search_description or "",
        "summary": _summary(article),
        "section": article.section,
        "tags": [],
        "reporterId": reporter_id,
        "reporterName": reporter_name,
        "publishedAt": published_at.isoformat() if published_at else "",
        "updatedAt": updated_at.isoformat() if updated_at else "",
        "editLevel": article.last_edit_level or "L1",
        "correctionNote": article.correction_note or "",
        "imageUrl": "",
        "imageCaption": "",
        "body": paragraphs,
    }


def _ingest_token_from_request(request) -> str:
    header_token = request.headers.get("X-CMS-Token", "").strip()
    if header_token:
        return header_token

    auth_header = request.headers.get("Authorization", "").strip()
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return ""


def _validate_intake_token(request):
    configured_token = os.getenv("CMS_AI_INTAKE_TOKEN", "").strip()
    if not configured_token:
        return JsonResponse(
            {
                "error": "CMS_AI_INTAKE_TOKEN is not configured.",
                "hint": "Set CMS_AI_INTAKE_TOKEN before using AI intake API.",
            },
            status=503,
        )
    provided = _ingest_token_from_request(request)
    if provided != configured_token:
        return JsonResponse({"error": "Invalid intake token."}, status=403)
    return None


def _build_body_html(raw_body: Any) -> str:
    if isinstance(raw_body, str):
        text = raw_body.strip()
        if not text:
            return ""
        if "<" in text and ">" in text:
            return text
        paragraphs = [segment.strip() for segment in text.split("\n") if segment.strip()]
        return "".join(f"<p>{escape(segment)}</p>" for segment in paragraphs)

    if isinstance(raw_body, list):
        paragraphs = [str(segment).strip() for segment in raw_body if str(segment).strip()]
        return "".join(f"<p>{escape(segment)}</p>" for segment in paragraphs)

    return ""


def _resolve_section(raw_section: Any) -> str:
    if not isinstance(raw_section, str):
        return Section.POLICY
    normalized = raw_section.strip().lower()
    if normalized in {choice[0] for choice in Section.choices}:
        return normalized
    return Section.POLICY


def _resolve_intent(raw_intent: Any) -> str:
    if not isinstance(raw_intent, str):
        return ArticleStatus.WRITING
    normalized = raw_intent.strip().lower()
    if normalized in AI_ALLOWED_INTENTS:
        return normalized
    return ArticleStatus.WRITING


def _next_unique_slug(parent: NewsroomHomePage, headline: str, preferred_slug: str) -> str:
    base = preferred_slug.strip() if preferred_slug else ""
    if not base:
        base = slugify(headline)[:80]
    if not base:
        base = "ai-draft"

    candidate = base
    suffix = 2
    while parent.get_children().filter(slug=candidate).exists():
        candidate = f"{base[:72]}-{suffix}"
        suffix += 1
    return candidate


def _resolve_reporter(reporter_username: Any):
    if not isinstance(reporter_username, str) or not reporter_username.strip():
        return None
    user_model = get_user_model()
    return user_model.objects.filter(username=reporter_username.strip()).first()


@require_GET
def api_articles_list(request):
    limit_raw = request.GET.get("limit", "50")
    try:
        limit = max(1, min(int(limit_raw), 100))
    except ValueError:
        limit = 50

    queryset = (
        ArticlePage.objects.live()
        .public()
        .filter(workflow_status__in=PUBLISHED_STATES)
        .select_related("reporter")
        .order_by("-first_published_at")[:limit]
    )
    items = [_to_payload(article) for article in queryset]

    return JsonResponse({"items": items, "count": len(items), "source": "wagtail"}, status=200)


@require_GET
def api_article_detail(request, slug: str):
    article = (
        ArticlePage.objects.live()
        .public()
        .filter(workflow_status__in=PUBLISHED_STATES, slug=slug)
        .select_related("reporter")
        .first()
    )
    if article is None:
        raise Http404("Article not found")

    return JsonResponse({"item": _to_payload(article), "source": "wagtail"}, status=200)


@csrf_exempt
@require_POST
@transaction.atomic
def api_ai_draft_intake(request):
    token_error = _validate_intake_token(request)
    if token_error is not None:
        return token_error

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    headline = str(payload.get("headline", "")).strip()
    external_id = str(payload.get("external_id", "")).strip()
    if not headline:
        return JsonResponse({"error": "`headline` is required."}, status=422)
    if not external_id:
        return JsonResponse({"error": "`external_id` is required."}, status=422)

    existing = ArticlePage.objects.filter(ai_external_id=external_id).first()
    if existing:
        return JsonResponse(
            {
                "idempotent": True,
                "article_id": existing.article_id,
                "slug": existing.slug,
                "workflow_status": existing.workflow_status,
                "admin_edit_url": f"/admin/pages/{existing.id}/edit/",
                "desk_queue_url": "/admin/newsroom/desk-queue/",
            },
            status=200,
        )

    home = NewsroomHomePage.objects.first()
    if home is None:
        return JsonResponse(
            {
                "error": "NewsroomHomePage is not initialized.",
                "hint": "Run `python manage.py bootstrap_cms_site` first.",
            },
            status=409,
        )

    intent = _resolve_intent(payload.get("intent"))
    section = _resolve_section(payload.get("section"))
    summary = str(payload.get("summary", "")).strip()
    preferred_slug = str(payload.get("slug", "")).strip()
    body_html = _build_body_html(payload.get("body", ""))
    if not body_html:
        return JsonResponse({"error": "`body` is required (string or string array)."}, status=422)

    reporter = _resolve_reporter(payload.get("reporter_username"))
    desk_editor = _resolve_reporter(payload.get("desk_editor_username"))
    slug_value = _next_unique_slug(home, headline, preferred_slug)

    article = ArticlePage(
        title=headline,
        slug=slug_value,
        search_description=summary[:255],
        body=body_html,
        section=section,
        workflow_status=intent,
        reporter=reporter,
        desk_editor=desk_editor,
        ai_external_id=external_id,
    )
    home.add_child(instance=article)
    article.save_revision()

    ArticleAuditLog.objects.create(
        article=article,
        actor=reporter,
        action="ai_ingest",
        from_status="",
        to_status=intent,
        details={
            "external_id": external_id,
            "intent": intent,
            "section": section,
            "model": payload.get("model", {}),
            "citations": payload.get("citations", []),
            "source_urls": payload.get("source_urls", []),
        },
    )

    return JsonResponse(
        {
            "idempotent": False,
            "article_id": article.article_id,
            "slug": article.slug,
            "workflow_status": article.workflow_status,
            "admin_edit_url": f"/admin/pages/{article.id}/edit/",
            "desk_queue_url": "/admin/newsroom/desk-queue/",
        },
        status=201,
    )

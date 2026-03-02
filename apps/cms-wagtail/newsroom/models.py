from __future__ import annotations

from uuid import uuid4
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


def generate_article_id() -> str:
    return f"ART-{timezone.localdate():%Y%m%d}-{uuid4().hex[:8].upper()}"


class ArticleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    WRITING = "writing", "Writing"
    DESK_REVIEW = "desk_review", "Desk Review"
    DESK_REWORK = "desk_rework", "Desk Rework"
    APPROVED = "approved", "Approved"
    SCHEDULED = "scheduled", "Scheduled"
    PUBLISHED = "published", "Published"
    PUBLISHED_UPDATED = "published_updated", "Published Updated"
    RETRACTED = "retracted", "Retracted"
    ARCHIVED = "archived", "Archived"


class EditLevel(models.TextChoices):
    L1 = "L1", "L1 (Minor)"
    L2 = "L2", "L2 (Important)"
    L3 = "L3", "L3 (Critical)"


class Section(models.TextChoices):
    ECONOMY = "economy", "Economy"
    SOCIETY = "society", "Society"
    POLICY = "policy", "Policy"


class NewsroomHomePage(Page):
    max_count = 1
    subpage_types = ["newsroom.ArticlePage"]
    parent_page_types = ["wagtailcore.Page"]

    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]


class ArticlePage(Page):
    parent_page_types = ["newsroom.NewsroomHomePage"]
    subpage_types: list[str] = []

    article_id = models.CharField(max_length=30, unique=True, default=generate_article_id, editable=False)
    ai_external_id = models.CharField(
        max_length=120,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text="Idempotency key from AI ingestion pipeline.",
    )
    section = models.CharField(max_length=24, choices=Section.choices, default=Section.POLICY)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reported_articles",
    )
    desk_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="desk_reviewed_articles",
    )
    workflow_status = models.CharField(
        max_length=24,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
    )
    last_edit_level = models.CharField(max_length=2, choices=EditLevel.choices, blank=True)
    scheduled_publish_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="예약 시간은 Asia/Seoul 기준으로 입력하고 UTC로 저장한다.",
    )
    correction_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="l3_followups",
        help_text="L3 정정/추후/반론 기사일 때 원기사를 연결한다.",
    )
    correction_note = models.TextField(blank=True)
    body = RichTextField(blank=True)
    published_revision_no = models.PositiveIntegerField(default=0, editable=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("section"),
                FieldPanel("reporter"),
                FieldPanel("desk_editor"),
                FieldPanel("workflow_status"),
                FieldPanel("last_edit_level"),
                FieldPanel("scheduled_publish_at"),
                FieldPanel("correction_of"),
                FieldPanel("correction_note"),
            ],
            heading="Editorial Metadata",
        ),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("article_id", partial_match=True),
        index.SearchField("title", partial_match=True),
        index.SearchField("body"),
    ]

    class Meta:
        permissions = (
            ("submit_desk_review", "Can move article to desk_review"),
            ("approve_article", "Can approve and publish article"),
            ("schedule_article", "Can schedule article"),
            ("retract_article", "Can retract article"),
            ("archive_article", "Can archive article"),
            ("apply_l2_update", "Can perform L2 published update"),
            ("create_l3_followup", "Can create L3 follow-up article"),
        )

    def clean(self) -> None:
        super().clean()

        previous: Optional["ArticlePage"] = None
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).only("slug", "live", "workflow_status").first()

        if previous and previous.live and self.slug != previous.slug:
            raise ValidationError({"slug": "Published article slug cannot be changed."})

        is_published_state = self.workflow_status in {
            ArticleStatus.PUBLISHED,
            ArticleStatus.PUBLISHED_UPDATED,
        }

        if previous and previous.live and is_published_state and not self.last_edit_level:
            raise ValidationError({"last_edit_level": "Select L1/L2/L3 when updating a published article."})

        if previous and previous.live and self.last_edit_level == EditLevel.L3 and not self.correction_of_id:
            raise ValidationError(
                {
                    "last_edit_level": "L3 cannot modify an already published article in-place. "
                    "Create a new article and connect it with correction_of."
                }
            )

        if self.correction_of_id and self.pk and self.correction_of_id == self.pk:
            raise ValidationError({"correction_of": "An article cannot reference itself as correction target."})

        if self.correction_of_id and self.last_edit_level != EditLevel.L3:
            raise ValidationError({"last_edit_level": "When correction_of is set, edit level must be L3."})

        if is_published_state and self.last_edit_level == EditLevel.L3 and not self.correction_of_id:
            raise ValidationError(
                {"correction_of": "L3 requires creating a new linked article with correction_of set."}
            )

    def __str__(self) -> str:
        return f"{self.article_id} - {self.title}"


class ArticleAuditLog(models.Model):
    article = models.ForeignKey(ArticlePage, on_delete=models.CASCADE, related_name="audit_logs")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cms_audit_events",
    )
    action = models.CharField(max_length=40)
    from_status = models.CharField(max_length=24, blank=True)
    to_status = models.CharField(max_length=24, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.article.article_id} {self.from_status}->{self.to_status} ({self.action})"

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page, Site

from newsroom.models import ArticleAuditLog, ArticlePage, ArticleStatus, EditLevel, NewsroomHomePage, Section
from newsroom.services import apply_transition


class NewsroomPolicyTests(TestCase):
    def setUp(self) -> None:
        self.user_model = get_user_model()

        self.reporter = self.user_model.objects.create_user(
            username="reporter_u",
            password="pw",
            is_staff=True,
        )
        self.desk = self.user_model.objects.create_user(
            username="desk_u",
            password="pw",
            is_staff=True,
        )
        self.eic = self.user_model.objects.create_user(
            username="eic_u",
            password="pw",
            is_staff=True,
        )

        Group.objects.create(name="reporter").user_set.add(self.reporter)
        Group.objects.create(name="desk").user_set.add(self.desk)
        Group.objects.create(name="editor_in_chief").user_set.add(self.eic)

        root = Page.get_first_root_node()
        self.home = NewsroomHomePage(title="Newsroom", slug="newsroom")
        root.add_child(instance=self.home)
        self.home.save_revision(user=self.eic).publish()

        Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": "testserver",
                "port": 80,
                "site_name": "Test Site",
                "root_page": self.home,
            },
        )

    def _create_article(
        self,
        *,
        title: str,
        slug: str,
        status: str = ArticleStatus.DRAFT,
        edit_level: str = "",
        live: bool = False,
    ) -> ArticlePage:
        page = ArticlePage(
            title=title,
            slug=slug,
            body="<p>Body text</p>",
            workflow_status=status,
            last_edit_level=edit_level,
            section=Section.POLICY,
            reporter=self.reporter,
            desk_editor=self.desk,
        )
        self.home.add_child(instance=page)
        revision = page.save_revision(user=self.eic)
        if live:
            revision.publish()
        return ArticlePage.objects.get(pk=page.pk).specific

    def test_published_slug_is_immutable(self):
        article = self._create_article(
            title="Published",
            slug="published-slug",
            status=ArticleStatus.PUBLISHED,
            edit_level=EditLevel.L1,
            live=True,
        )
        article.slug = "changed-slug"

        with self.assertRaises(ValidationError) as exc:
            article.full_clean()

        self.assertIn("slug", exc.exception.message_dict)

    def test_published_update_requires_edit_level(self):
        article = self._create_article(
            title="Published 2",
            slug="published-two",
            status=ArticleStatus.PUBLISHED,
            edit_level=EditLevel.L1,
            live=True,
        )
        article.workflow_status = ArticleStatus.PUBLISHED_UPDATED
        article.last_edit_level = ""

        with self.assertRaises(ValidationError) as exc:
            article.full_clean()

        self.assertIn("last_edit_level", exc.exception.message_dict)

    def test_in_place_l3_update_is_blocked(self):
        article = self._create_article(
            title="Published 3",
            slug="published-three",
            status=ArticleStatus.PUBLISHED,
            edit_level=EditLevel.L1,
            live=True,
        )
        article.workflow_status = ArticleStatus.PUBLISHED_UPDATED
        article.last_edit_level = EditLevel.L3

        with self.assertRaises(ValidationError) as exc:
            article.full_clean()

        self.assertIn("last_edit_level", exc.exception.message_dict)

    def test_l3_followup_must_reference_origin(self):
        origin = self._create_article(
            title="Origin",
            slug="origin-article",
            status=ArticleStatus.PUBLISHED,
            edit_level=EditLevel.L1,
            live=True,
        )

        with self.assertRaises(ValidationError):
            self._create_article(
                title="Invalid Followup",
                slug="invalid-followup-article",
                status=ArticleStatus.PUBLISHED,
                edit_level=EditLevel.L3,
                live=False,
            )

        valid_followup = ArticlePage(
            title="Valid Followup",
            slug="valid-followup-article",
            body="<p>Followup body</p>",
            workflow_status=ArticleStatus.DRAFT,
            last_edit_level=EditLevel.L3,
            correction_of=origin,
            section=Section.POLICY,
            reporter=self.reporter,
            desk_editor=self.desk,
        )
        self.home.add_child(instance=valid_followup)
        valid_followup.save_revision(user=self.eic)

    def test_reporter_cannot_approve(self):
        article = self._create_article(
            title="Desk Review 1",
            slug="desk-review-one",
            status=ArticleStatus.DESK_REVIEW,
            live=False,
        )

        with self.assertRaises(PermissionDenied):
            apply_transition(
                article=article,
                target_status=ArticleStatus.APPROVED,
                actor=self.reporter,
            )

    def test_desk_can_approve_and_audit_log_is_created(self):
        article = self._create_article(
            title="Desk Review 2",
            slug="desk-review-two",
            status=ArticleStatus.DESK_REVIEW,
            live=False,
        )

        apply_transition(
            article=article,
            target_status=ArticleStatus.APPROVED,
            actor=self.desk,
        )

        article.refresh_from_db()
        self.assertEqual(article.workflow_status, ArticleStatus.APPROVED)
        self.assertTrue(
            ArticleAuditLog.objects.filter(
                article=article,
                from_status=ArticleStatus.DESK_REVIEW,
                to_status=ArticleStatus.APPROVED,
            ).exists()
        )

    def test_scheduled_transition_requires_future_datetime(self):
        article = self._create_article(
            title="Desk Review 3",
            slug="desk-review-three",
            status=ArticleStatus.DESK_REVIEW,
            live=False,
        )

        with self.assertRaises(ValidationError):
            apply_transition(
                article=article,
                target_status=ArticleStatus.SCHEDULED,
                actor=self.desk,
                scheduled_at=timezone.now() - timedelta(minutes=1),
            )

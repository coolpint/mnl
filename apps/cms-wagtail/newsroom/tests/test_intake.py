from __future__ import annotations

import json
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.models import Page, Site

from newsroom.models import ArticleAuditLog, ArticlePage, ArticleStatus, NewsroomHomePage


class NewsroomIntakeApiTests(TestCase):
    def setUp(self) -> None:
        os.environ["CMS_AI_INTAKE_TOKEN"] = "test-ingest-token"
        user_model = get_user_model()
        self.reporter = user_model.objects.create_user(
            username="ai_reporter",
            password="pw",
            is_staff=True,
        )
        self.desk = user_model.objects.create_user(
            username="ai_desk",
            password="pw",
            is_staff=True,
        )

        root = Page.get_first_root_node()
        self.home = NewsroomHomePage(title="Newsroom", slug="newsroom")
        root.add_child(instance=self.home)
        self.home.save_revision().publish()

        Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": "testserver",
                "port": 80,
                "site_name": "Test Site",
                "root_page": self.home,
            },
        )

    def tearDown(self) -> None:
        os.environ.pop("CMS_AI_INTAKE_TOKEN", None)

    def _post(self, payload: dict, token: str = "test-ingest-token"):
        return self.client.post(
            "/api/v1/newsroom/intake/ai-draft/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CMS_TOKEN=token,
        )

    def test_intake_requires_valid_token(self):
        response = self._post({"headline": "x", "external_id": "id-1", "body": "content"}, token="invalid")
        self.assertEqual(response.status_code, 403)

    def test_intake_creates_writing_article(self):
        payload = {
            "external_id": "draft-001",
            "headline": "AI Draft Headline",
            "summary": "Quick summary",
            "section": "policy",
            "intent": "writing",
            "reporter_username": "ai_reporter",
            "desk_editor_username": "ai_desk",
            "body": ["first paragraph", "second paragraph"],
            "citations": [{"url": "https://example.com/source-1"}],
            "model": {"provider": "openai", "name": "gpt-5"},
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertFalse(data["idempotent"])

        article = ArticlePage.objects.get(ai_external_id="draft-001")
        self.assertEqual(article.workflow_status, ArticleStatus.WRITING)
        self.assertEqual(article.reporter.username, "ai_reporter")
        self.assertIn("first paragraph", article.body)
        self.assertTrue(
            ArticleAuditLog.objects.filter(
                article=article,
                action="ai_ingest",
                to_status=ArticleStatus.WRITING,
            ).exists()
        )

    def test_intake_supports_desk_review_intent(self):
        payload = {
            "external_id": "draft-002",
            "headline": "Desk Review Ready",
            "intent": "desk_review",
            "body": "content",
        }
        response = self._post(payload)
        self.assertEqual(response.status_code, 201)

        article = ArticlePage.objects.get(ai_external_id="draft-002")
        self.assertEqual(article.workflow_status, ArticleStatus.DESK_REVIEW)

    def test_intake_is_idempotent_by_external_id(self):
        payload = {
            "external_id": "draft-003",
            "headline": "Same request",
            "body": "content",
        }
        first = self._post(payload)
        second = self._post(payload)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(ArticlePage.objects.filter(ai_external_id="draft-003").count(), 1)

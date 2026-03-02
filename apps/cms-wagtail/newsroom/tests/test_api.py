from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.models import Page, Site

from newsroom.models import ArticlePage, ArticleStatus, EditLevel, NewsroomHomePage, Section


class NewsroomApiTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.editor = user_model.objects.create_user(
            username="api_editor",
            password="pw",
            is_staff=True,
            is_superuser=True,
        )

        root = Page.get_first_root_node()
        self.home = NewsroomHomePage(title="Newsroom", slug="newsroom")
        root.add_child(instance=self.home)
        self.home.save_revision(user=self.editor).publish()

        Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": "testserver",
                "port": 80,
                "site_name": "Test Site",
                "root_page": self.home,
            },
        )

    def _create_article(self, *, title: str, slug: str, status: str, live: bool) -> ArticlePage:
        page = ArticlePage(
            title=title,
            slug=slug,
            body="<p>API body text.</p>",
            workflow_status=status,
            last_edit_level=EditLevel.L1 if status in (ArticleStatus.PUBLISHED, ArticleStatus.PUBLISHED_UPDATED) else "",
            section=Section.POLICY,
            reporter=self.editor,
            desk_editor=self.editor,
        )
        self.home.add_child(instance=page)
        revision = page.save_revision(user=self.editor)
        if live:
            revision.publish()
        return ArticlePage.objects.get(pk=page.pk).specific

    def test_list_only_returns_published_variants(self):
        self._create_article(
            title="Published Article",
            slug="published-article",
            status=ArticleStatus.PUBLISHED,
            live=True,
        )
        self._create_article(
            title="Updated Article",
            slug="updated-article",
            status=ArticleStatus.PUBLISHED_UPDATED,
            live=True,
        )
        self._create_article(
            title="Draft Article",
            slug="draft-article",
            status=ArticleStatus.DRAFT,
            live=False,
        )

        response = self.client.get("/api/v1/newsroom/articles/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["count"], 2)
        slugs = {item["slug"] for item in payload["items"]}
        self.assertIn("published-article", slugs)
        self.assertIn("updated-article", slugs)
        self.assertNotIn("draft-article", slugs)

    def test_detail_returns_payload_by_slug(self):
        article = self._create_article(
            title="Detail Article",
            slug="detail-article",
            status=ArticleStatus.PUBLISHED,
            live=True,
        )

        response = self.client.get(f"/api/v1/newsroom/articles/{article.slug}/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["item"]["slug"], article.slug)
        self.assertEqual(payload["item"]["id"], article.article_id)

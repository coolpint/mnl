from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import GroupPagePermission, Page, Site

from newsroom.models import ArticlePage, ArticleStatus, EditLevel, NewsroomHomePage, Section


class Command(BaseCommand):
    help = "Create default NewsroomHomePage/Site and seed sample articles."

    def handle(self, *args, **options):
        root = Page.get_first_root_node()

        newsroom_home = NewsroomHomePage.objects.first()
        if newsroom_home is None:
            newsroom_home = NewsroomHomePage(
                title="Newsroom CMS Home",
                slug="newsroom",
                intro="Thread-B Wagtail newsroom workspace",
            )
            root.add_child(instance=newsroom_home)
            newsroom_home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created NewsroomHomePage (/newsroom/)"))
        else:
            self.stdout.write(self.style.SUCCESS("NewsroomHomePage already exists"))

        default_site = Site.objects.filter(is_default_site=True).first()
        if default_site is None:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                site_name="moneynlaw CMS",
                root_page=newsroom_home,
                is_default_site=True,
            )
            self.stdout.write(self.style.SUCCESS("Created default Site (localhost:8000)"))
        else:
            default_site.root_page = newsroom_home
            default_site.hostname = "localhost"
            default_site.port = 8000
            default_site.save(update_fields=["root_page", "hostname", "port"])
            self.stdout.write(self.style.SUCCESS("Updated default Site root page to NewsroomHomePage"))

        page_permission_policy = {
            "reporter": ("add_page", "change_page", "view_page"),
            "desk": ("add_page", "change_page", "publish_page", "view_page"),
            "editor_in_chief": (
                "add_page",
                "change_page",
                "delete_page",
                "publish_page",
                "lock_page",
                "unlock_page",
                "bulk_delete_page",
                "view_page",
            ),
        }
        page_content_type = ContentType.objects.get(app_label="wagtailcore", model="page")
        for role, perm_types in page_permission_policy.items():
            group = Group.objects.filter(name=role).first()
            if group is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skip GroupPagePermission for '{role}' (group missing). Run bootstrap_cms_rbac first."
                    )
                )
                continue

            GroupPagePermission.objects.filter(
                group=group,
                page=newsroom_home,
                permission__content_type=page_content_type,
            ).exclude(
                permission__codename__in=perm_types
            ).delete()
            for permission_codename in perm_types:
                permission = Permission.objects.filter(
                    content_type=page_content_type,
                    codename=permission_codename,
                ).first()
                if permission is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Missing permission '{permission_codename}' for wagtailcore.page."
                        )
                    )
                    continue
                GroupPagePermission.objects.get_or_create(
                    group=group,
                    page=newsroom_home,
                    permission=permission,
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"GroupPagePermission synced for '{role}': {', '.join(perm_types)}"
                )
            )

        if ArticlePage.objects.exists():
            self.stdout.write(self.style.SUCCESS("Article sample seed skipped (already exists)."))
            return

        user = get_user_model().objects.order_by("id").first()

        sample_pages = [
            {
                "title": "Sample Draft: Market Opening Brief",
                "slug": "sample-draft-market-opening-brief",
                "status": ArticleStatus.DRAFT,
                "edit_level": "",
                "section": Section.ECONOMY,
            },
            {
                "title": "Sample Desk Review: Court Filing Summary",
                "slug": "sample-desk-review-court-filing-summary",
                "status": ArticleStatus.DESK_REVIEW,
                "edit_level": "",
                "section": Section.SOCIETY,
            },
            {
                "title": "Sample Published: Regulatory Q&A Update",
                "slug": "sample-published-regulatory-qna-update",
                "status": ArticleStatus.PUBLISHED,
                "edit_level": EditLevel.L1,
                "section": Section.POLICY,
            },
        ]

        for seed in sample_pages:
            page = ArticlePage(
                title=seed["title"],
                slug=seed["slug"],
                body="<p>Sample body content for CMS verification.</p>",
                workflow_status=seed["status"],
                last_edit_level=seed["edit_level"],
                section=seed["section"],
                reporter=user,
                desk_editor=user,
            )
            newsroom_home.add_child(instance=page)

            if seed["status"] == ArticleStatus.PUBLISHED:
                page.first_published_at = timezone.now()
                page.last_published_at = timezone.now()
                page.published_revision_no = 1
                page.save(update_fields=["first_published_at", "last_published_at", "published_revision_no"])
                page.save_revision(user=user).publish()
            else:
                page.save_revision(user=user)

        self.stdout.write(self.style.SUCCESS("Seeded sample ArticlePage data (draft/review/published)."))

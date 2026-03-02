from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import desk_queue_view, transition_article_view


@hooks.register("register_admin_urls")
def register_newsroom_admin_urls():
    return [
        path("newsroom/desk-queue/", desk_queue_view, name="newsroom_desk_queue"),
        path(
            "newsroom/desk-queue/<int:page_id>/transition/",
            transition_article_view,
            name="newsroom_transition_article",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_newsroom_menu_item():
    return MenuItem("Desk Queue", reverse("newsroom_desk_queue"), icon_name="doc-full", order=220)

from django.urls import path

from .api_views import api_ai_draft_intake, api_article_detail, api_articles_list


urlpatterns = [
    path("intake/ai-draft/", api_ai_draft_intake, name="newsroom_api_ai_draft_intake"),
    path("articles/", api_articles_list, name="newsroom_api_articles"),
    path("articles/<slug:slug>/", api_article_detail, name="newsroom_api_article_detail"),
]

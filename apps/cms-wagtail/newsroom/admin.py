from django.contrib import admin

from .models import ArticleAuditLog


@admin.register(ArticleAuditLog)
class ArticleAuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "article", "action", "from_status", "to_status", "actor")
    list_filter = ("action", "to_status", "created_at")
    search_fields = ("article__article_id", "article__title", "actor__username")

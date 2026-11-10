from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("voyage", "author", "subject", "rating_overall", "published_at")
    list_filter = ("published_at",)

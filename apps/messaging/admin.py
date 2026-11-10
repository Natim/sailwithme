from django.contrib import admin

from .models import AbuseReport, Conversation, Message, UserBlock


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_group", "updated_at")
    inlines = [MessageInline]


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")


@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported_user", "created_at")

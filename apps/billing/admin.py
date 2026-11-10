from django.contrib import admin

from .models import Membership


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "active", "valid_until", "created_at")
    list_filter = ("plan", "active")

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "skill_level", "nautical_miles", "crew_directory_visible")
    search_fields = ("user__email", "nationality", "home_port")
    list_filter = ("role", "skill_level")

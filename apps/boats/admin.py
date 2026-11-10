from django.contrib import admin

from .models import Boat, BoatPhoto


class BoatPhotoInline(admin.TabularInline):
    model = BoatPhoto
    extra = 0


@admin.register(Boat)
class BoatAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "boat_type", "length_ft", "berths")
    search_fields = ("name", "owner__email")
    inlines = [BoatPhotoInline]

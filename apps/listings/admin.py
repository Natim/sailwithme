from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from apps.core.widgets import ConfiguredOSMWidget

from .models import Listing, ListingApplication, Port, RoutePage, SearchAlert, Voyage


@admin.register(Port)
class PortAdmin(GISModelAdmin):
    gis_widget = ConfiguredOSMWidget
    list_display = ("name", "country", "slug")
    search_fields = ("name", "slug")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "kind", "status", "date_from", "featured")
    list_filter = ("status", "kind", "programme_type")
    search_fields = ("title", "author__email")


@admin.register(ListingApplication)
class ListingApplicationAdmin(admin.ModelAdmin):
    list_display = ("listing", "applicant", "status", "created_at")
    list_filter = ("status",)


@admin.register(Voyage)
class VoyageAdmin(admin.ModelAdmin):
    list_display = ("title", "listing", "skipper", "reviews_open")
    filter_horizontal = ("crew",)


@admin.register(SearchAlert)
class SearchAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "active", "created_at")


@admin.register(RoutePage)
class RoutePageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

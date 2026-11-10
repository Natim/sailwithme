from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("", views.listing_search, name="search"),
    path("mine/", views.MyListingsView.as_view(), name="mine"),
    path("new/", views.listing_create, name="create"),
    path("alerts/", views.save_search_alert, name="save_alert"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("routes/<slug:slug>/", views.RouteSEOPageView.as_view(), name="route_page"),
    path("<int:pk>/", views.ListingDetailView.as_view(), name="detail"),
    path("<int:pk>/apply/", views.listing_apply, name="apply"),
    path("applications/<int:app_id>/<str:action>/", views.application_decide, name="application_decide"),
]

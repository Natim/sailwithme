from django.urls import path

from . import views

app_name = "boats"

urlpatterns = [
    path("", views.BoatListView.as_view(), name="list"),
    path("new/", views.boat_create, name="create"),
    path("<uuid:pk>/", views.BoatDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", views.boat_edit, name="edit"),
    path("<uuid:pk>/delete/", views.boat_delete, name="delete"),
    path("<uuid:pk>/photos/", views.boat_add_photo, name="add_photo"),
    path("photos/<uuid:photo_pk>/delete/", views.boat_photo_delete, name="delete_photo"),
]

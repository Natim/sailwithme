from django.urls import path

from . import views

app_name = "boats"

urlpatterns = [
    path("", views.BoatListView.as_view(), name="list"),
    path("new/", views.boat_create, name="create"),
    path("<int:pk>/", views.BoatDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.boat_edit, name="edit"),
    path("<int:pk>/photos/", views.boat_add_photo, name="add_photo"),
]

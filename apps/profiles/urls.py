from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("me/", views.profile_me, name="me"),
    path("edit/<str:section>/", views.profile_edit_section, name="edit_section"),
    path("directory/", views.ProfileDirectoryView.as_view(), name="directory"),
    path("<uuid:pk>/", views.ProfileDetailView.as_view(), name="detail"),
]

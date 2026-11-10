from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("voyage/<uuid:voyage_id>/subject/<uuid:subject_id>/", views.write_review, name="write"),
    path("<uuid:review_id>/respond/", views.respond_review, name="respond"),
]

from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("voyage/<int:voyage_id>/subject/<int:subject_id>/", views.write_review, name="write"),
    path("<int:review_id>/respond/", views.respond_review, name="respond"),
]

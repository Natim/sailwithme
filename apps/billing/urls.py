from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/<str:plan>/", views.checkout, name="checkout"),
    path("success/", views.checkout_success, name="success"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
]

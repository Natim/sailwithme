from django.conf import settings


def site_settings(request):
    return {
        "SITE_NAME": "Sails with Me",
        "STRIPE_PUBLIC_KEY": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
    }

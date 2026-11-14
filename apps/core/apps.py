from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self):
        from django.conf import settings
        from django.db.utils import OperationalError, ProgrammingError

        domain = getattr(settings, "SITE_DOMAIN", None)
        if not domain:
            return
        from django.contrib.sites.models import Site

        try:
            Site.objects.update_or_create(
                pk=settings.SITE_ID,
                defaults={"domain": domain, "name": "Sail with Me"},
            )
        except (OperationalError, ProgrammingError):
            return

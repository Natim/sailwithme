from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel


class MembershipPlan(models.TextChoices):
    CREW_SEASON = "crew_season", _("Crew Pass — season")
    CREW_LIFETIME = "crew_lifetime", _("Crew Pass — lifetime")
    SKIPPER_PLUS = "skipper_plus", _("Skipper+")
    IDENTITY = "identity", _("Identity verified")


class Membership(UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    plan = models.CharField(max_length=32, choices=MembershipPlan.choices)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def is_current(self) -> bool:
        if not self.active:
            return False
        if self.valid_until and self.valid_until < timezone.now():
            return False
        return True

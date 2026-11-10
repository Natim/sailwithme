from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel


class BoatType(models.TextChoices):
    MONOHULL = "monohull", _("Monohull")
    CATAMARAN = "catamaran", _("Catamaran")
    TRIMARAN = "trimaran", _("Trimaran")
    OTHER = "other", _("Other")


class Boat(UUIDModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="boats",
    )
    name = models.CharField(max_length=128)
    boat_type = models.CharField(max_length=16, choices=BoatType.choices, default=BoatType.MONOHULL)
    model_name = models.CharField(max_length=128, blank=True)
    length_ft = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)
    flag = models.CharField(max_length=64, blank=True)
    berths = models.PositiveSmallIntegerField(default=2)
    equipment = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BoatPhoto(UUIDModel):
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="boats/")
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

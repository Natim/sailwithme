from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel

from .iso_weeks import iso_week_range_to_dates, period_months_label


class Port(UUIDModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=128)
    country = models.CharField(max_length=64, blank=True)
    location = gis_models.PointField(geography=True, srid=4326)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def lat(self):
        return self.location.y if self.location else None

    @property
    def lng(self):
        return self.location.x if self.location else None


class ListingKind(models.TextChoices):
    CREW_WANTED = "crew_wanted", _("Looking for crew")
    BERTH_WANTED = "berth_wanted", _("Looking for a berth")


class ProgrammeType(models.TextChoices):
    TRANSATLANTIC = "transatlantic", _("Transatlantic")
    TRANSPACIFIC = "transpacific", _("Transpacific")
    MEDITERRANEAN = "mediterranean", _("Mediterranean")
    DELIVERY = "delivery", _("Delivery")
    COASTAL = "coastal", _("Coastal")
    SEASON = "season", _("Full season")


class ListingStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    FULL = "full", _("Complete")
    EXPIRED = "expired", _("Expired")
    WITHDRAWN = "withdrawn", _("Withdrawn")


class Listing(UUIDModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )
    boat = models.ForeignKey(
        "boats.Boat",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="listings",
    )
    kind = models.CharField(max_length=16, choices=ListingKind.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    programme_type = models.CharField(max_length=32, choices=ProgrammeType.choices)
    departure_port = models.ForeignKey(
        Port,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="departures",
    )
    arrival_port = models.ForeignKey(
        Port,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="arrivals",
    )
    departure_point = gis_models.PointField(geography=True, srid=4326)
    arrival_point = gis_models.PointField(geography=True, srid=4326)
    departure_name = models.CharField(max_length=128)
    arrival_name = models.CharField(max_length=128)
    flexibility_nm = models.PositiveIntegerField(default=50, help_text="Rayon en milles nautiques")
    year = models.PositiveSmallIntegerField()
    week_from = models.PositiveSmallIntegerField()
    week_to = models.PositiveSmallIntegerField()
    date_from = models.DateField()
    date_to = models.DateField()
    duration_days = models.PositiveSmallIntegerField(null=True, blank=True)
    berths_available = models.PositiveSmallIntegerField(default=1)
    daily_contribution_eur = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Participation indicative (non commerciale)",
    )
    min_skill_level = models.CharField(max_length=16, blank=True)
    languages_on_board = models.JSONField(default=list, blank=True)
    requirements = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=ListingStatus.choices,
        default=ListingStatus.DRAFT,
    )
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "-created_at"]
        indexes = [
            models.Index(fields=["status", "date_from", "date_to"]),
            models.Index(fields=["programme_type"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("listings:detail", kwargs={"pk": self.pk})

    def period_months_display(self) -> str:
        if self.date_from and self.date_to:
            return period_months_label(self.date_from, self.date_to)
        from .iso_weeks import period_months_from_weeks

        return period_months_from_weeks(self.year, self.week_from, self.week_to)

    def save(self, *args, **kwargs):
        if self.year and self.week_from and self.week_to:
            self.date_from, self.date_to = iso_week_range_to_dates(
                self.year, self.week_from, self.week_to
            )
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == ListingStatus.PUBLISHED and self.date_to >= timezone.now().date()


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Declined")
    WITHDRAWN = "withdrawn", _("Withdrawn")


class ListingApplication(UUIDModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_applications",
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("listing", "applicant")]
        ordering = ["-created_at"]


class Voyage(UUIDModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="voyages")
    skipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skippered_voyages",
    )
    crew = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="crew_voyages",
        blank=True,
    )
    title = models.CharField(max_length=200, blank=True)
    started_at = models.DateField(null=True, blank=True)
    ended_at = models.DateField(null=True, blank=True)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    reviews_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"Voyage #{self.pk}"


class SearchAlert(UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_alerts",
    )
    name = models.CharField(max_length=128, blank=True)
    departure_lat = models.FloatField(null=True, blank=True)
    departure_lng = models.FloatField(null=True, blank=True)
    departure_radius_nm = models.PositiveIntegerField(default=100)
    arrival_lat = models.FloatField(null=True, blank=True)
    arrival_lng = models.FloatField(null=True, blank=True)
    arrival_radius_nm = models.PositiveIntegerField(default=100)
    week_from = models.PositiveSmallIntegerField(null=True, blank=True)
    week_to = models.PositiveSmallIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    programme_type = models.CharField(max_length=32, blank=True)
    kind = models.CharField(max_length=16, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RoutePage(UUIDModel):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    meta_description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    departure_port = models.ForeignKey(
        Port,
        on_delete=models.SET_NULL,
        null=True,
        related_name="route_pages_departure",
    )
    arrival_port = models.ForeignKey(
        Port,
        on_delete=models.SET_NULL,
        null=True,
        related_name="route_pages_arrival",
    )

    def __str__(self):
        return self.title

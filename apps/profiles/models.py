import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse

ALLOWED_PROFILE_PHOTO_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def profile_photo_upload_to(instance: "Profile", filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".jpeg":
        suffix = ".jpg"
    if suffix not in ALLOWED_PROFILE_PHOTO_SUFFIXES:
        suffix = ".jpg"
    return f"profiles/{instance.public_id}{suffix}"


class ProfileRole(models.TextChoices):
    SKIPPER = "skipper", "Skipper"
    CREW = "crew", "Équipier"
    BOTH = "both", "Les deux"


class SkillLevel(models.TextChoices):
    BEGINNER = "beginner", "Débutant"
    COASTAL = "coastal", "Côtier"
    OFFSHORE = "offshore", "Hauturier"
    PRO_SKIPPER = "pro_skipper", "Skipper professionnel"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=16, choices=ProfileRole.choices, default=ProfileRole.CREW)
    photo = models.ImageField(upload_to=profile_photo_upload_to, blank=True)
    bio = models.TextField(blank=True)
    nationality = models.CharField(max_length=64, blank=True)
    languages = models.JSONField(default=list, blank=True)
    home_port = models.CharField(max_length=128, blank=True)
    skill_level = models.CharField(
        max_length=16,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
    )
    nautical_miles = models.PositiveIntegerField(default=0)
    ocean_crossings = models.PositiveSmallIntegerField(default=0)
    certifications = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    non_smoker = models.BooleanField(default=False)
    pets_ok = models.BooleanField(default=True)
    vegetarian_friendly = models.BooleanField(default=False)
    availability_notes = models.TextField(blank=True)
    crew_directory_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Profile({self.user.email})"

    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"pk": self.user_id})

    def completeness_score(self) -> int:
        fields = [
            self.bio,
            self.nationality,
            self.languages,
            self.home_port,
            self.photo,
            self.availability_notes,
        ]
        filled = sum(1 for f in fields if f)
        if self.nautical_miles or self.ocean_crossings:
            filled += 1
        if self.certifications or self.skills:
            filled += 1
        return min(100, int(filled / 8 * 100))

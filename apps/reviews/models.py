from django.conf import settings
from django.db import models
from django.utils import timezone


class Review(models.Model):
    voyage = models.ForeignKey(
        "listings.Voyage",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    rating_overall = models.PositiveSmallIntegerField()
    rating_seamanship = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_reliability = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_atmosphere = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_safety = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_commitment = models.PositiveSmallIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    response = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("voyage", "author", "subject")]
        ordering = ["-created_at"]

    def try_publish(self):
        counterpart = Review.objects.filter(
            voyage=self.voyage,
            author=self.subject,
            subject=self.author,
        ).first()
        if counterpart:
            now = timezone.now()
            if not self.published_at:
                self.published_at = now
            if not counterpart.published_at:
                counterpart.published_at = now
                counterpart.save(update_fields=["published_at"])
            self.save(update_fields=["published_at"])

    @property
    def is_visible(self):
        if self.published_at:
            return True
        age = timezone.now() - self.created_at
        return age.days >= 14

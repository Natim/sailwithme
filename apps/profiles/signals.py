from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.billing.services import grant_registration_crew_trial

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        grant_registration_crew_trial(instance)

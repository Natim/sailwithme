from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Doctor


@receiver(post_save, sender=get_user_model())
def create_superuser_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            doctor_profile = Doctor(user=instance)
            doctor_profile.user.is_doctor = True
            doctor_profile.user.save()
            doctor_profile.save()
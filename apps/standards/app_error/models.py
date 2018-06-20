from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from password_policies.models import PasswordChangeRequired

@receiver(post_save, sender=User)
def force_password_change(sender, instance, created, **kwargs):
    if created:
        PasswordChangeRequired.objects.create(user=instance)

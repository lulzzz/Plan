from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, verbose_name="Location")
    company = models.CharField(max_length=100, blank=True, verbose_name="Company")
    department = models.CharField(max_length=100, blank=True, verbose_name="Department")
    title = models.CharField(max_length=100, blank=True, verbose_name="Job Title")

    is_test_user = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

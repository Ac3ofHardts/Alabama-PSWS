from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    signup_confirmation = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = 'Admin'
        SCIENCE = 'Science'
        SUPERSCIENCE = 'SuperScience'
        USER = 'User'

    role = models.CharField(
            max_length=20,
            choices=Role.choices,
            default=Role.USER,
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    instance.profile.save()

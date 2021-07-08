from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

# Create your models here.

class Station(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(default="", max_length=50)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    grid = models.CharField(max_length=6, null=True)
    elevation = models.FloatField(blank=True, null=True)
    
    create_date = datetime.now()

    station_id = models.CharField(max_length=10, null=True, blank=True)
    station_pass = models.CharField(max_length=20, null=True, blank=True)
    
    last_rID = models.IntegerField(default=0)

    last_alive = models.DateTimeField(null=True)


    def get_username(self):
        return self.username
    User.add_to_class("__str__", get_username)

    class StationStatus(models.TextChoices):
            ONLINE = "Online",
            POSSIBLYONLINE = "Possiblyonline",
            OFFLINE = "Offline"

    station_status = models.CharField(
            max_length=20,
            choices=StationStatus.choices,
            default=StationStatus.OFFLINE,
    )

    def __str__(self):
        return self.nickname

@receiver(post_save, sender=User)
def update_station_signal(sender, instance, created, **kwargs):
    if created:
        Station.objects.get_or_create(user=instance)
    instance.profile.save()

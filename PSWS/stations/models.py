from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Station(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    grid = models.CharField(max_length=6)
    elevation = models.FloatField()

    def __str__(self):
        return self.user.username

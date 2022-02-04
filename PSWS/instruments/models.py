from django.db import models

# Create your models here.
class Instrument(models.Model):
    instrument = models.CharField(max_length=40)

from django.db import models

from stations.models import Station
from observations.models import Observation

# Create your models here.

class Experiment(models.Model):
    observation     = models.ManyToManyField(Observation, verbose_name="Observation", blank=True)
    product         = models.ManyToManyField("analysis.product", verbose_name="Product", blank=True)
    path            = models.CharField(max_length=40)

class Product(models.Model):
    # experiment      = models.ManyToManyField(Experiment, verbose_name="Experiment", blank=True)
    fileName        = models.CharField("File", max_length=40)



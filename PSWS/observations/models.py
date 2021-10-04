from django.db import models

from stations.models import Station
from instruments.models import Instrument
from bands.models import Band
from datatypes.models import DataType


class Observation(models.Model):
    dataType = models.ManyToManyField(DataType, blank=True)
    dataRate = models.IntegerField()
    centerFrequency = models.IntegerField(default=-1)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    instrument = models.ManyToManyField(Instrument, blank=True)
    band = models.ManyToManyField(Band, blank=True)
    size = models.IntegerField()
    fileName = models.CharField(max_length=40)
    path = models.CharField(max_length=40)

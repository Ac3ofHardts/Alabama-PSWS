from django.db import models

from stations.models import Station
from instruments.models import Instrument
from bands.models import Band
from datatypes.models import DataType
from centerfrequencies.models import CenterFrequency

class Observation(models.Model):
    dataType = models.ManyToManyField(DataType, verbose_name="Data type", blank=True)
    dataRate = models.IntegerField("Data rate")
    #centerFrequency = models.IntegerField("Center frequency", default=-1)
    centerFrequency = models.ManyToManyField(CenterFrequency, verbose_name="Center Frequency", blank=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True)
    #instrument = models.ManyToManyField(Instrument, blank=True)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, default=1)
    band = models.ManyToManyField(Band, verbose_name="Band", blank=True)
    size = models.BigIntegerField()
    fileName = models.CharField("File", max_length=40)
    path = models.CharField(max_length=40)
    startDate = models.DateTimeField("Start Date")
    endDate = models.DateTimeField("End Date", null=True, blank=True)

    def __str__(self):
        return 'Observation_' + self.station.station_id + '_' + self.fileName

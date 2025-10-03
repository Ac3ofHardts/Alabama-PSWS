from django.db import models

from instrumenttypes.models import InstrumentType
from stations.models import Station

# Create your models here.
class Instrument(models.Model):
    instrument = models.CharField(max_length=40)
    instrumenttype = models.ForeignKey(InstrumentType, on_delete=models.CASCADE, null=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, default=1)
    serialNo = models.CharField(max_length=60, null=True, blank=True)
    dateAdded = models.DateTimeField("Date Added", null=True, blank=True)
    dateRemoved = models.DateTimeField("Date Removed", null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    nickname = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.instrument + "\n(" + self.instrumenttype.instrumentType + ")"

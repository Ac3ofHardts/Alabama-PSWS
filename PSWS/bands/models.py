from django.db import models

# Create your models here.
class Band(models.Model):
    band = models.IntegerField(verbose_name = 'Band (m)')

    def __str__(self):
        return str(self.band) + ' m'

    class Meta:
        verbose_name = 'Band (m)'
        verbose_name_plural = 'Bands (m)'

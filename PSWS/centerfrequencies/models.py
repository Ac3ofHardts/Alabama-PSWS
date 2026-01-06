from django.db import models

# Create your models here.
class CenterFrequency(models.Model):
    centerFrequency = models.DecimalField(max_digits = 5, decimal_places = 3, verbose_name="Center Frequency (MHz)")
    
    def __str__(self):
       return str(self.centerFrequency) + ' MHz' 

    class Meta:
        verbose_name = 'Center Frequency (MHz)'
        verbose_name_plural = 'Center Frequencies (MHz)'

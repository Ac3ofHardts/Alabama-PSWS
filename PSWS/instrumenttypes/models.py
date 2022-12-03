from django.db  import models

class InstrumentType(models.Model):
    instrumentType = models.CharField(max_length=40)

    def __str__(self):
      return self.instrumentType

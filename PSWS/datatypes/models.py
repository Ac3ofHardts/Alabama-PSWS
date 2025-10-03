from django.db import models

# Create your models here.
class DataType(models.Model):
    dataType = models.CharField(max_length=40)


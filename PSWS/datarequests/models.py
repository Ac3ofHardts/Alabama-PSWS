from django.db import models
from accounts.models import Profile

# Create your models here.
class DataRequest(models.Model):
    requestID = models.AutoField(primary_key=True)
    timestart = models.DateTimeField()
    timestop = models.DateTimeField()
    requester = models.ManyToManyField(Profile)

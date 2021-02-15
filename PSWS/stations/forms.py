from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from stations.models import Station

class StationCreationForm(ModelForm):
    station_nickname = forms.CharField(max_length=30)
    grid = forms.CharField(max_length=6)
    elevation = forms.FloatField() #min and max values?
    antenna_1 = forms.CharField(max_length=64) #required me to include default - not sure why
    antenna_2 = forms.CharField(max_length=64, blank=True)
    street_addres = forms.CharField(max_length=75, blank=True)
    city = forms.CharField(max_length=75, blank=True)
    state = forms.CharField(max_length=15, blank=True)
    postal_code = forms.CharField(max_length=15, blank=True)
    phone_number = forms.CharField(max_length=20, blank=True)

    class Meta:
        model = Station
        fields = ('station_nickname', 'grid', 'elevation', 'antenna_1', 'antenna_2', 'street_address', 'city', 'state', 'postal_code', 'phone_number')

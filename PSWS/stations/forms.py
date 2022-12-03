from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from stations.models import Station

# Form used to register new stations
class StationCreationForm(forms.ModelForm):
    nickname = forms.CharField(max_length=30)
    grid = forms.CharField(label='Maidenhead Grid Square', max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Ex: AA11aa'}))
    elevation = forms.FloatField(required=False, help_text='meters above sea level')
    antenna_1 = forms.CharField(max_length=64, required=False)
    antenna_2 = forms.CharField(max_length=64, required=False)
    street_address = forms.CharField(max_length=75, required=False)
    city = forms.CharField(max_length=32, required=False)
    state = forms.CharField(max_length=15, required=False)
    postal_code = forms.CharField(max_length=15, required=False)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Station
        fields = ('nickname', 'grid', 'elevation', 'antenna_1', 'antenna_2', 'street_address', 'city', 'state', 'postal_code', 'phone_number')

# Form used to edit the data pertaining to a specific station
class EditStationForm(forms.ModelForm):
    nickname = forms.CharField(max_length=30)
    grid = forms.CharField(label='Maidenhead Grid Square', max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Ex: AA11aa'}))
    elevation = forms.FloatField(required=False, help_text='meters above sea level')
    antenna_1 = forms.CharField(max_length=64,required=False)
    antenna_2 = forms.CharField(max_length=64, required=False)
    street_address = forms.CharField(max_length=75,required=False)
    city = forms.CharField(max_length=32,required=False)
    state = forms.CharField(max_length=15,required=False)
    postal_code = forms.CharField(max_length=15,required=False)
    phone_number = forms.CharField(max_length=20,required=False)
    
    class Meta:
        model = Station
        fields = ('nickname', 'grid', 'elevation', 'antenna_1', 'antenna_2', 'street_address', 'city', 'state', 'postal_code', 'phone_number', )

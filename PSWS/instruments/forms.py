from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from instruments.models import Instrument
from instrumenttypes.models import InstrumentType

#from crispy_forms.helper import FormHelper

# Form used to register new instrument
class InstrumentCreationForm(forms.ModelForm):

    instrument     = forms.CharField(max_length=40, required=True)
    instrumenttype = forms.ModelChoiceField(queryset=InstrumentType.objects.all(), required=True)
    dateAdded      = forms.DateTimeField(label="Date instrument added", help_text='format YYYY-MM-DD', required=False)

    class Meta:
        model = Instrument

        fields = ('instrument', 'dateAdded',  'nickname', 'serialNo', 'status',
                  'instrumenttype' )

# Form used to edit the data pertaining to a specific instrument
class EditInstrumentForm(forms.ModelForm):

    instrument     = forms.CharField(max_length=40, required=True)
    instrumenttype = forms.ModelChoiceField(queryset=InstrumentType.objects.all(), required=True)
    dateAdded      = forms.DateTimeField(label="Date instrument added", help_text='format YYYY-MM-DD', required=False)
    dateRemoved    = forms.DateTimeField(label="Date instrument removed", help_text='format YYYY-MM-DD', required=False)

    class Meta:
        model =  Instrument
        fields = ('instrument', 'dateAdded', 'dateRemoved', 'nickname', 'serialNo', 'status',
                  'instrumenttype')


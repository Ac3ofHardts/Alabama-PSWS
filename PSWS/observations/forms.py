from django import forms
from django.forms.widgets import DateInput, DateTimeInput

class DateTimeInput(forms.DateTimeInput):
    input_type = 'date'

class DateTimeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput())
    end_date = forms.DateField(input_formats=['%d/%m/%Y %H:%i'])

    class Meta:
        fields = ('start_date', 'end_date')

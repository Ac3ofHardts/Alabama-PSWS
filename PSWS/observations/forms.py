from django import forms
from django.forms.widgets import DateInput, DateTimeInput
from django.core.exceptions import ValidationError


class DateTimeInput(forms.DateTimeInput):
    input_type = 'date'

class DateTimeForm(forms.Form):
    start_date = forms.DateTimeField(label='Start Date (UTC)', widget=forms.DateTimeInput(attrs={'placeholder': 'YYYY-mm-dd HH:MM'}), 
            input_formats=[
                '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
                '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
                '%Y-%m-%d',             # '2006-10-25'
                '%Y/%m/%d %H:%M',       # '2006/10/25 14:30'
                '%Y/%m/%d',             # '2006/10/25'
                '%m/%d/%Y %H:%M:%S',    # '10/25/2006 14:30:59'
                '%m/%d/%Y %H:%M',       # '10/25/2006 14:30'
                '%m/%d/%Y',             # '10/25/2006'
                '%m/%d/%y %H:%M:%S',    # '10/25/06 14:30:59'
                '%m/%d/%y %H:%M',       # '10/25/06 14:30'
                '%m/%d/%y'              # '10/25/06'
            ])

    end_date = forms.DateTimeField(label='End Date (UTC)', widget=forms.DateTimeInput(attrs={'placeholder': 'YYYY-mm-dd HH:MM'}),
            input_formats=[
                '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
                '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
                '%Y-%m-%d',             # '2006-10-25'
                '%Y/%m/%d %H:%M',       # '2006/10/25 14:30'
                '%Y/%m/%d',             # '2006/10/25'
                '%m/%d/%Y %H:%M:%S',    # '10/25/2006 14:30:59'
                '%m/%d/%Y %H:%M',       # '10/25/2006 14:30'
                '%m/%d/%Y',             # '10/25/2006'
                '%m/%d/%y %H:%M:%S',    # '10/25/06 14:30:59'
                '%m/%d/%y %H:%M',       # '10/25/06 14:30'
                '%m/%d/%y'              # '10/25/06'
            ])

    class Meta:
        fields = ('start_date', 'end_date')

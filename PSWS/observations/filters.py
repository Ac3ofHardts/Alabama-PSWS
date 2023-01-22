import django_filters

from .models import Observation
from stations.models import Station
from bands.models import Band
from centerfrequencies.models import CenterFrequency
from instruments.models import Instrument
from instrumenttypes.models import InstrumentType

class ObservationFilter(django_filters.FilterSet):
    #centerFrequency = django_filters.NumberFilter()
    #centerFrequency__gt = django_filters.NumberFilter(field_name='centerFrequency', lookup_expr='gt')
    #centerFrequency__lt = django_filters.NumberFilter(field_name='centerFrequency', lookup_expr='lt')

    station = django_filters.ModelChoiceFilter(queryset=Station.objects.all(), label='Station Nickname')

#    band = django_filters.filters.ModelMultipleChoiceFilter(
#            field_name='band__band',
#            to_field_name='band',
#            queryset=Band.objects.all(),
#            label='Band',
#    )

    instrument = django_filters.filters.ModelMultipleChoiceFilter(
            field_name='instrument__instrumenttype__instrumentType',
            to_field_name='instrumentType',
            queryset=InstrumentType.objects.all(),
            label='Instrument Type',
    )
    
    centerFrequency = django_filters.filters.ModelMultipleChoiceFilter(
            field_name='centerFrequency__centerFrequency',
            to_field_name='centerFrequency',
            queryset=CenterFrequency.objects.all(),
            label='Center Frequency',
    )
   
    startDate__gte = django_filters.DateFilter(field_name='startDate', lookup_expr='date__gte', label='Start Date')
    endDate__lte   = django_filters.DateFilter(field_name='endDate',   lookup_expr='date__lte', label='End Date')

    class Meta:
        model = Observation
        fields = ['instrument', 'centerFrequency', 'station',
        #'band'
         ]

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

    # Select a single station to filter the query
    station = django_filters.ModelChoiceFilter(queryset=Station.objects.all(), label='Station Nickname')

#    band = django_filters.filters.ModelMultipleChoiceFilter(
#            field_name='band__band',
#            to_field_name='band',
#            queryset=Band.objects.all(),
#            label='Band',
#    )

    # Select one or more instrument types to include in query
    instrument = django_filters.filters.ModelMultipleChoiceFilter(
            field_name='instrument__instrumenttype__instrumentType',
            to_field_name='instrumentType',
            queryset=InstrumentType.objects.all(),
            label='Instrument Type',
    )
    
    # Select one or more center frequencies to include in query
    centerFrequency = django_filters.filters.ModelMultipleChoiceFilter(
            field_name='centerFrequency__centerFrequency',
            to_field_name='centerFrequency',
            queryset=CenterFrequency.objects.all(),
            label='Center Frequency',
    )
    
    # Filter for observations beginning after the start date or before the end date
    startDate__gte = django_filters.DateFilter(field_name='startDate', lookup_expr='date__gte', label='Start Date')
    endDate__lte   = django_filters.DateFilter(field_name='endDate',   lookup_expr='date__lte', label='End Date')

    # Filter for observations from stations located within a rectangle set by the user's desired coordinates
    # Need to add check/warning in case of east < west, north < south, or invalid lat/long values
    # Should we allow empty fields?
    topLeftLat__lte = django_filters.NumberFilter(field_name='station__latitude', lookup_expr='lte', label='Northmost Latitude')
    bottomRightLat__gte = django_filters.NumberFilter(field_name='station__latitude', lookup_expr='gte', label='Southmost Latitude')
    topLeftLong__gte = django_filters.NumberFilter(field_name='station__longitude', lookup_expr='gte', label='Westmost Longitude')
    bottomRightLong__lte = django_filters.NumberFilter(field_name='station__longitude', lookup_expr='lte', label='Eastmost Longitude')

    class Meta:
        model = Observation
        fields = ['instrument', 'centerFrequency', 'station',
        #'band'
         ]

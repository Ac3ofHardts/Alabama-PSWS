import django_tables2 as tables
from .models import Station
from django_tables2 import A
from instruments.models import Instrument

class StationTable(tables.Table):
    class Meta:
        model = Station
        template_name = "django_tables2/bootstrap.html"
        fields = ("station_id", "user", "nickname", "grid", "elevation", "station_status",)

class FilteredStationTable(tables.Table):
    station_id = tables.LinkColumn('station_details', args=[A('id')])

    class Meta:
        model = Station
        template_name = "django_tables2/bootstrap.html"
        fields = ("station_id", "nickname", "grid", "elevation", "antenna_1", "antenna_2", "station_status",)

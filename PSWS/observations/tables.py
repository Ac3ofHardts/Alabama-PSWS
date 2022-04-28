import django_tables2 as tables
from .models import Observation
from django_tables2 import A

class ObservationTable(tables.Table):
    fileName = tables.LinkColumn('download_file', args=[A('id')])

    class Meta:
        model = Observation
        template_name = "django_tables2/bootstrap.html"
        fields = ("dataType", "dataRate", "centerFrequency", "station", "instrument", "band", "size", "fileName", "startDate", "endDate")
        

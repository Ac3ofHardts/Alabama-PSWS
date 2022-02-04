import django_tables2 as tables
from .models import Observation

class ObservationTable(tables.Table):
    class Meta:
        model = Observation
        template_name = "django_tables2/bootstrap.html"
        fields = ("dataType", "dataRate", "centerFrequency", "station", "instrument", "band", "size", "fileName", )
        

import django_tables2 as tables
from .models import Observation
from django_tables2 import A

class ObservationTable(tables.Table):
    fileName = tables.LinkColumn('download_file', args=[A('id')], verbose_name='File/Observation')
    startDate = tables.DateTimeColumn(format="c", verbose_name="Start (UTC)")
    endDate   = tables.DateTimeColumn(format="c", verbose_name="End (UTC)")
    #fileName =  tables.Column(verbose_name="File/Observation")

    class Meta:
        model = Observation
        template_name = "django_tables2/bootstrap.html"
       # fields = ("dataType", "dataRate", "centerFrequency", "station", "instrument", "band", "size", "fileName", "startDate", "endDate")
        fields = ("dataRate", "centerFrequency", "station", "instrument.instrument", "size", "fileName", "startDate", "endDate")
        

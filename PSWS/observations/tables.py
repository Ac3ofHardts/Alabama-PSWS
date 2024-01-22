import django_tables2 as tables
from .models import Observation
from django_tables2 import A

class TruncatedTextColumn(tables.Column):
    def render(self, value):
        if len(value) > 15:
            return value[0:15] + '...'
        return str(value)

class CustomBooleanColumn(tables.BooleanColumn):
    def render(self, value):
        if value != None:
            return str("Yes")
        return str("No")

class ObservationTable(tables.Table):
    #fileName = tables.LinkColumn('download_file', args=[A('id')], verbose_name='File/Observation') 
    size = tables.Column(verbose_name='Size (MB)')
    fileName = tables.LinkColumn('select_download_range', args=[A('id')], verbose_name='File/Observation')
    startDate = tables.DateTimeColumn(format="Y-m-d H:i:s", verbose_name="Start (UTC)")
    endDate   = tables.DateTimeColumn(format="Y-m-d H:i:s", verbose_name="End (UTC)")
    instrument = TruncatedTextColumn(accessor=A('instrument.instrument'))
    plotExists = CustomBooleanColumn(accessor=A('plotFile'), verbose_name="Plot")

    def render_size(self, value):
        converted_size = float(value)
        converted_size = converted_size / 1000000.0
        return "{:,.4f}".format(converted_size)
        #return "%s MB" % converted_size / 1000000.0

    class Meta:
        model = Observation
        template_name = "django_tables2/bootstrap.html"
       # fields = ("dataType", "dataRate", "centerFrequency", "station", "instrument", "band", "size", "fileName", "startDate", "endDate")
        fields = ("dataRate", "centerFrequency", "station", "instrument", "size", "fileName", "plotExists", "startDate", "endDate")
        attrs = {"class": "obsTable"}
        

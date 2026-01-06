
import django_tables2 as tables
from .models import Instrument
from django_tables2 import A
from django_tables2.utils import Accessor
from instrumenttypes.models import InstrumentType

class InstrumentTable(tables.Table):
   # id = tables.LinkColumn('instrument_details', args=[A('station_id')])
    id =  tables.LinkColumn('instrument_details', args=[A('id')])
    instrument_type = tables.Column(accessor=Accessor('instrumenttype.instrumentType'))

    class Meta:
        model = Instrument
        template_name = "django_tables2/bootstrap.html"
        fields = ("id", "instrument", "nickname", "serialNo",
           "instrument_type" )

#
class FilteredInstrumentsTable (tables.Table):  # used for display after adding new intrument
    id = tables.LinkColumn('instrument_details', args=[A('station_id')])

    class Meta:
        model = Instrument
        template_name = "django_tables2/bootstrap.html"
        field = ("id", "instrument",  "instrumenttype_id", "nickname", "serialNo", "status", "status", )


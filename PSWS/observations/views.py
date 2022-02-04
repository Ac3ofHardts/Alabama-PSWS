from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableView

from .models import Observation
from .tables import ObservationTable


# Create your views here.

@method_decorator(login_required, name='dispatch')
# Display a list of all observations in the database
class ObservationListView(SingleTableView):
    table_class = ObservationTable
    queryset = Observation.objects.all()
    template_name = "observation_list.html"

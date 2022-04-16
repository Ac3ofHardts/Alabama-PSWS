from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableView
from django.http import HttpResponse

from .models import Observation
from .tables import ObservationTable


# Create your views here.
def download_file(request, id=None):
    observation = get_object_or_404(Observation, id=id)

    fl_path = observation.path
    filename = observation.fileName
    fl_path = fl_path + filename

    fl = open(fl_path, 'rb')

    mime_type, _ = mimetypes.guess_type(fl_path)
    # potentially need to change content_type="application/x-tar"
    response = HttpResponse(fl, content_type=mime_type)
    # response = HttpResponse(fl, content_type="application/x-tar")
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response



@method_decorator(login_required, name='dispatch')
# Display a list of all observations in the database
class ObservationListView(SingleTableView):
    table_class = ObservationTable
    queryset = Observation.objects.all()
    template_name = "observation_list.html"

# Authors:   Nicholas Muscolino, Anderson Liddle, Cole Robbins
# University of Alabama, Apr-May 2022 with funding from NSF Grant 80NSSC21K1772
# Modified by W. Engelke, July 2022

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from django.http import HttpResponse

from .models import Observation
from .tables import ObservationTable
from .filters import ObservationFilter
from .forms import DateTimeForm

import shutil
import os
import mimetypes

import digital_rf as drf
import h5py

# Create your views here.
def download_file(request, id=None):
    observation = get_object_or_404(Observation, id=id)

    fl_path = observation.path
    filename = observation.fileName
    fl_path = fl_path + filename

    try:  # does the requested tar file exist?
        fl = open(fl_path, 'rb')
    except IOError:  # file is not there, see if this is request for download of  DRF dataset
        obs = get_object_or_404(Observation, id=id)
        fl_path =  obs.fileName
        file_extension  = os.path.splitext(fl_path)[1]
        # here we skip doing the tar if the file is already in zip format
        # In version 1, this is magnetometer
        if file_extension == ".zip":
            fl_path = observation.path + "/" + observation.fileName # correct this
            fl = open(fl_path, 'rb')
            mime_type, _ = mimetypes.guess_type(fl_path)
            response = HttpResponse(fl, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % observation.fileName
            return response

        total_path = obs.path
        zip_path = "/home/ziptemp/" + total_path.rsplit('/')[2] +   \
                   "/temp/" + total_path.rsplit('/')[3]
        print("tar file to: " + zip_path)

        shutil.make_archive(zip_path, 'zip', total_path)
        command = "chmod 777 " + zip_path + ".zip"  # this is to allow leter cleanup
        os.system(command)
        fl = open(zip_path + '.zip', 'rb')

        # The following replaces the original tar/gzip code as it produces a
        # zip file without the internal directory structure
        fl = open(zip_path + '.zip', 'rb')
        mime_type, _ = mimetypes.guess_type(zip_path+'.zip')
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'], = "attachment; filename=%s" % fl_path+'.zip'

        return response

    mime_type, _ = mimetypes.guess_type(fl_path)
    # potentially need to change content_type="application/x-tar"
    response = HttpResponse(fl, content_type=mime_type)
    # response = HttpResponse(fl, content_type="application/x-tar")
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

#def download_range(request,id=None):
#   
#    observation = get_object_or_404(Observation, id=id)
#
#    fl_path = observation.path
#    filename = observation.fileName
#    fl_path = fl_path + filename
#    zip_path = fl_path + '.tar'
#
#    shutil.make_archive(fl_path, 'tar', fl_path)
#
#    fl = open(zip_path, 'rb')
#
#    mime_type, _ = mimetypes.guess_type(fl_path)
#    #potentially need to change content_type="application/x-tar"
#    response = HttpResponse(fl, content_type=mime_type)
#    #response = HttpResponse(fl, content_type="application/tar")
#    response['Content-Disposition'] = "attachment; filename=%s" % filename
#    return response
#    # Create your views here.

def download_range(request, id=None, start=None, end=None):
    observation = get_object_or_404(Observation, id=id)

    fl_path = observation.path
    filename = observation.fileName
    full_path = fl_path + filename

    #zip_path = "/home/ziptemp/" + fl_path.rsplit('/')[2] + \
    #        "/temp/" + filename[:3] + start + "-" + end

    zip_name = filename[:16] + "-" + start + "-" + end + ".zip"
    zip_path = "/home/ziptemp/" + zip_name
    print(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipF:

        zipF.write(full_path + "/ch0/drf_properties.h5", \
                 arcname = "ch0/drf_properties.h5")

        zipF.write(full_path + "/ch0/metadata/dmd_properties.h5", \
                 arcname = "ch0/metadata/dmd_properties.h5")

        for file in os.listdir(full_path + '/ch0'):

            if '-' not in file: continue

            file_name = str(file[0:10])
            print(file_name)
            if (start <= file_name <= end):
                for sub_file in os.listdir(full_path + '/ch0/' + file):
                    zipF.write(full_path + "/ch0/" + file + "/" + sub_file,\
                            arcname = "ch0/" + file + "/" + sub_file)

        for file in os.listdir(full_path + '/ch0/metadata'):
            file_name = str(file[0:10])
            if (start <= file_name <= end):
                for sub_file in os.listdir(full_path + '/ch0/metadata/' + file):
                    zipF.write(full_path + "/ch0/metadata/" + file + "/" + sub_file, \
                            arcname = "ch0/metadata/" + file + "/" + sub_file)

        fl = open(zip_path, 'rb')

        os.remove(zip_path)

        mime_type, _ = mimetypes.guess_type(zip_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % zip_name

        return response

def get_date_range(request, id=None):
    observation = get_object_or_404(Observation, id=id)

    fl_path = observation.path
    filename = observation.fileName

    drf_data = drf.DigitalRFReader(fl_path + filename)
    start, end = drf_data.get_bounds('ch0')
    startDate = datetime.fromtimestamp(start / 10)
    endDate = datetime.fromtimestamp(end / 10)
    print(str(startDate) + " " + str(endDate))

    start = datetime.fromtimestamp(start / 10)
    start_string = start.strftime("%Y-%m-%d")
    end = datetime.fromtimestamp(end / 10)
    end_string = end.strftime("%Y-%m-%d")

    print(start_string)
    print(end_string)



    return redirect("/observations/observation_list/")


def select_download_range(request, id=None):
    observation = get_object_or_404(Observation, id=id)
    form_class = DateTimeForm
    return render(request, 'select_download_range.html', {'observation': observation, 'form': form_class})

#@method_decorator(login_required, name='dispatch')
# Display a list of all observations in the database
#class ObservationListView(SingleTableView):
#    table_class = ObservationTable
#    queryset = Observation.objects.all()
#    template_name = "observation_list.html"

@method_decorator(login_required, name='dispatch')
# Display a list of all observations in the database
class ObservationListView(SingleTableMixin, FilterView):
    table_class = ObservationTable
    model = Observation
    template_name = "observation_list.html"
    filterset_class = ObservationFilter
    paginate_by = 4

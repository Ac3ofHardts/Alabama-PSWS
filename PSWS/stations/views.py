from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from datetime import datetime
from stations.models import Station
from stations.forms import StationCreationForm
from django.contrib import messages

from stations.calculate_latitude import CalculateLatitude
from stations.calculate_longitude import CalculateLongitude
from .forms import EditStationForm
from .tokens import station_activation_token

import os
import logging
logger = logging.getLogger(__name__)

# Create your views here.

@login_required
# Display a list of the logged in user's stations
def my_stations_list_view(request):
    return render(request, 'my_stations_list.html')

@login_required
# Display the list of all registered stations
def station_list_view(request):
    all_stations = Station.objects.all()
    context = {'all_stations': all_stations}
    return render(request, 'stations.html', context)

@login_required
# Display more detailed information about a station
def station_details_view(request, id=None):
    station = get_object_or_404(Station, id=id, user=request.user)

    all_stations = Station.objects.all()
    context = {'station': station}
    return render(request, 'station_details.html', context)

@login_required
# Allow a user to register a new station
def add_station_view(request):
    if request.method == "POST":
        form = StationCreationForm(request.POST)
        if form.is_valid():
            station = form.save(commit=False)
            station.user_id = request.user.id
            
            # Determine new station's ID number
            if Station.objects.latest('create_date') == None:
                new_id_number = 1
            else:
                new_id_number = Station.objects.latest('create_date').id + 1
            
            station.station_id = 'N' + str(new_id_number).zfill(6)
            station.station_pass = station_activation_token.make_token(request.user).replace('-', station.station_pass[0])[4:36]
            station.nickname = form.cleaned_data.get('nickname')
            station.grid = form.cleaned_data.get('grid')
            station.latitude = CalculateLatitude.calculate_latitude(station.grid)
            station.longitude = CalculateLongitude.calculate_longitude(station.grid)
            station.elevation = form.cleaned_data.get('elevation')
            station.antenna_1 = form.cleaned_data.get('antenna_1')
            station.antenna_2 = form.cleaned_data.get('antenna_2')
            station.street_address = form.cleaned_data.get('street_address')
            station.city = form.cleaned_data.get('city')
            station.state = form.cleaned_data.get('state')
            station.postal_code = form.cleaned_data.get('postal_code')
            station.phone_number = form.cleaned_data.get('phone_number')
            station.create_date = datetime.now()
            station.save()
            os.system('/bin/stationcreation ' + station.station_id + ' ' + station.station_pass)
            return redirect('stations')
    else:
        form = StationCreationForm()

    return render(request, 'add_station.html', {'form': form})

@login_required
# Allow a user to edit the data of a specific station
def update_station_view(request, id=None):
    station = get_object_or_404(Station, id=id, user=request.user)

    if request.method == 'POST':
        form = EditStationForm(request.POST, request.FILES, instance=station)
        #logger.error("POST request received")
        #form = EditStationForm(request.POST, instance=request.Station.station)
        if form.is_valid():
            #logger.error(request.station)
            station.nickname = form.cleaned_data.get('nickname')
            station.grid = form.cleaned_data.get('grid')
            station.latitude = CalculateLatitude.calculate_latitude(station.grid)
            station.longitude = CalculateLongitude.calculate_longitude(station.grid)
            station.elevation = form.cleaned_data.get('elevation')
            station.antenna_1 = form.cleaned_data.get('antenna_1')
            station.antenna_2 = form.cleaned_data.get('antenna_2')
            station.street_address = form.cleaned_data.get('street_address')
            station.city = form.cleaned_data.get('city')
            station.state = form.cleaned_data.get('state')
            station.postal_code = form.cleaned_data.get('postal_code')
            station.phone_number = form.cleaned_data.get('phone_number')
            station.save()
            messages.success(request, 'Your station has been updated!')
            return redirect('stations')
        else:
            form = EditStationForm(instance=station)
            messages.error(request, 'Issue updating information.')
            return render(request, 'station_update.html', {'form': form, 'station': station})
    else:
        form = EditStationForm(instance=station)
        return render(request, 'station_update.html', {'form': form, 'station': station})

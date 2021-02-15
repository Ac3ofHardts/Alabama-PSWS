from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from datetime import datetime
from stations.models import Station

# Create your views here.

@login_required
def station_list_view(request):
    return render(request, 'stations.html')

def add_station_view(request):
    if request.method == "POST":
        form = StationCreationForm(request.POST)
        if form.is_valid():
            station = form.save()
            station.refresh_from_db()
            station.station.station_nickname = form.cleaned_data.get('station_nickname')
            station.station.grid = form.cleaned_data.get('grid')
            station.station.elevation = form.cleaned_data.get('elevation')
            station.station.antenna_1 = form.cleaned_data.get('antenna_1')
            station.station.antenna_2 = form.cleaned_data.get('antenna_2')
            station.station.street_address = form.cleaned_data.get('street_address')
            station.station.city = form.cleaned_data.get('city')
            station.station.state = form.cleaned_data.get('state')
            station.station.postal_code = form.cleaned_data.get('postal_code')
            station.station.phone_number = form.cleaned_data.get('phone_number')
            station.station.create_date = datetime.now()
            station.station.station_status = form.station_status[2]
            station.save()
    else:
        form = StationCreationForm()
    return render(request, 'add_station.html', {'form':form})

#used to update station
class StationUpdate(UpdateView):
    model = Station
    fields = ['station_nickname', 'grid', 'elevation', 'antenna_1', 'antenna_2', 'street_address', 'city', 'state', 'postal_code', 'phone_number']
    template_name = 'update_station.html' 

from django.shortcuts import render
from django.http import HttpResponse

from datetime import datetime, timedelta, timezone

from stations.models import Station

#Declaring time cutoffs here since will probably change in the future
onlineCutoffHours = 24
possiblyOnlineCutoffHours = 120 #5 days

# Create your views here.
def analysis_view(request):
    return render(request, 'analysis.html')

def updateStatus():
    #Update Station status of all stations before displaying
    AliveCutoff = datetime.now(timezone.utc) - timedelta(hours=onlineCutoffHours)
    DeadCutoff = datetime.now(timezone.utc) - timedelta(hours=possiblyOnlineCutoffHours)
    for instance in Station.objects.all():
        if (instance.last_alive is None):
            instance.last_alive = datetime(2000,1,1,tzinfo=timezone.utc)
        if (instance.last_alive < DeadCutoff):
            instance.station_status = "Offline"
        elif (instance.last_alive < AliveCutoff):
            instance.station_status = "PossiblyOnline"
        else:
            instance.station_status = "Online"
        instance.save()

def analysis_map(request):
    updateStatus()
 #   mapbox_access_token = 'pk.eyJ1IjoiYWI0ZWotMSIsImEiOiJjazB1MTRmMTAwamVlM2Jwb2pheWx2cWpmIn0.cGZbctIFT5jSgBi0jBPk3w'
    mapbox_access_token = 'pk.eyJ1Ijoicm9sbHRpZGUiLCJhIjoiY2tueXFmMXhzMGt1MTJ1cDZ4YXkzOXJ3aiJ9.1HmCO6w6W-3r7Ou2HpRaMg'
    online_stations = Station.objects.filter(station_status="Online")
    possiblyonline_stations = Station.objects.filter(station_status="PossiblyOnline")
    offline_stations = Station.objects.filter(station_status="Offline")
    return render(request, 'analysis_map.html',
      { 'mapbox_access_token' : mapbox_access_token,
          'online_stations' : online_stations,
          'possiblyonline_stations' : possiblyonline_stations,
          'offline_stations' : offline_stations,
        } )

from django.shortcuts import render, redirect
from rest_framework import permissions
from rest_framework import generics
from .serializers import StationSerializer, HeartbeatSerializer
from stations.models import Station
from datarequests.models import DataRequest
from rest_framework.response import Response
from datetime import datetime, timedelta, timezone

#Declaring time cutoffs here since will probably change in the future
onlineCutoffHours = 24
possiblyOnlineCutoffHours = 120 #5 days


"""
API method of listing all stations and their attributes
To modify what is shown, modify the Serializer
In addition to displaying, this will also calculate whether
a specific station is alive or dead based on current time and the
last_alive time of the station.
May wish to change this to only update station status at a certain
time interval since it requires a loop of all station objects
"""
class StationList(generics.ListAPIView):
    queryset = Station.objects.all()
    #permission_classes = [permissions.IsAuthenticated]
    serializer_class = StationSerializer

    def get(self, request, format=None):
        """
        Return a list of all stations
        """

        #Update Station status of all stations before displaying
        AliveCutoff = datetime.now(timezone.utc) - timedelta(hours=onlineCutoffHours)
        DeadCutoff = datetime.now(timezone.utc) - timedelta(hours=possiblyOnlineCutoffHours)
        for instance in Station.objects.all():
            if (instance.last_alive < DeadCutoff): 
                instance.station_status = "Offline"
            elif (instance.last_alive < AliveCutoff):
                instance.station_status = "PossiblyOnline"
            else:
                instance.station_status = "Online"
            instance.save()
    
        return self.list(request)

"""
API that takes a POST or PUT that includes a station ID and Password
If valid, it will update the station's last_alive variable
A successful request will return 200, if there is a newer data request than
the last one fielded by the station, the response body will also include the 
timestamps of the data request
"""
class StationHeartbeat(generics.UpdateAPIView):
    queryset = Station.objects.all()
    serializer_class = HeartbeatSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        rID = request.data.get("station_id")
        rPass = request.data.get("station_pass")

        #Try to get specific station object
        try:
            instance = Station.objects.get(station_id = rID)
        except Station.DoesNotExist:
            return Response(status=404)

        #Make sure that password is valid
        if (instance.station_pass == rPass):
            #Update last alive
            instance.last_alive = datetime.now(timezone.utc)
            instance.save()

            #Grab latest data request
            dataReqInst = DataRequest.objects.latest('requestID')
            #Check if station has fielded this yet -- NOTE -- This functionality may change
            #Depending on how we want to handle a station that has missed multiple requests
            if(dataReqInst.requestID > instance.last_rID):
                instance.last_rID = dataReqInst.requestID
                instance.save()
                return Response({'timestart': dataReqInst.timestart, 'timestop': dataReqInst.timestop})
            else:
                return Response(status=200)  
        #Password did not match, return unauthorized
        return Response(status=401)

# psws_addOBS.py
# Add observation (where upload was detected by psws_watch) to
# Observations table

import os, sys
#  admin to use Djago ORM for db updating
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'PSWS.PSWS.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from django.db import models
django.setup()
from centerfrequencies.models import *
from observations.models import *
#import datetime

from datetime import timezone
from datetime import datetime as dt


def writeLog(theMessage):
    timestamp = dt.now(timezone.utc).isoformat()[0:19]
    f = open("/home/bengelke/Documents/watchdog.log", "a")
    f.write(timestamp + " " + theMessage + "\n")
    f.close()

# Arguments are: (1) datarate in samples/sec, (2) observation size in bytes, (3) filename ,
#  (4)  path, (5) station_id, (6) instrument, (7) start date, (8) end date

#print ('Argument List:', str(sys.argv))
dataRate = str(sys.argv[1])
obsSize = str (sys.argv[2])
fileName = str (sys.argv[3])
path = str (sys.argv[4])

station_name  = str(sys.argv[5])
theStationQS = Station.objects.filter(station_id=station_name)
print("found station:",theStationQS)
#print("values:",theStationQS.values())
print("id by item:",theStationQS.values()[0]["id"])
station_id = theStationQS.values()[0]["id"]

station_instance = Station.objects.get(station_id = station_name)

# update last_alive for this station
station_instance.last_alive = dt.now(timezone.utc)
# the station_status will update by itself when queried.
station_instance.save()
writeLog("Updated last alive for " + station_name + " to " + str(dt.now(timezone.utc)))

instrument_name = str(sys.argv[6])

if Instrument.objects.filter(instrument_id=instrument_name).exists():
    # We've been given the instrument id, so pull data using ID
    theInstrumentQS = Instrument.objects.filter(instrument_id=instrument_name, station_id=station_id)
else:
    # Given instrument name, so pull data using name
    theInstrumentQS = Instrument.objects.filter(instrument=instrument_name, station_id=station_id)

#print("found instrument:",theInstrumentQS)
try:
    instrument_id = theInstrumentQS.values()[0]["id"]
except IndexError as e:
    # the instrument given is not assigned to this station
    writeLog("ERROR. User specified " + station_name + " & " + instrument_name + "; no database match")
    exit()

startDate =  str (sys.argv[7])
# ensure database knows about UTC timezone
startDateTZ = dt.strptime(startDate, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
endDate = str (sys.argv[8])
endDateTZ = dt.strptime(endDate, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
cfid_list=[]

for  c in range(9, 17): # handles up to 8 center frequencies in this version
    try:
      #cfid_list.append(str(sys.argv[c]))
      theFreq = str(sys.argv[c])
      print("look up cfid ",theFreq)
      this_cfid = CenterFrequency.objects.filter(centerFrequency=theFreq).values('id')
      #print("found cfid:",this_cfid)
      cfid_list.append(this_cfid)
    except Exception as ex:
      #print("Exception:",str(ex))
      print("center freq ids found:", c-8)
      break

print("cfids:",cfid_list)
#sname = station_id
obs_list =  Observation.objects.filter(fileName = fileName, station_id=station_id, instrument_id=instrument_id) # doe this OBS already exist?
if len(obs_list) == 0:   # this is a new observation
    theObs  = Observation(dataRate=dataRate,size=obsSize,fileName=fileName,path=path, \
        #      instrument_id=instrument_id, station_id=station_id, startDate=startDateTZ, endDate=endDateTZ)
              startDate=startDateTZ, endDate=endDateTZ, \
              station_id = station_id, instrument_id = instrument_id )

    theObs.save()
    for this_cfid in cfid_list: # add one or more center frequencies in this datase
        theObs.centerFrequency.add(this_cfid)
        theObs.save()
              #theObs.centerFrequency.add(cfid) # this creates entry in intersection table
              #theObs.save()
else:  # this  observation is already in database. update endDate
    obsPtr = obs_list[0].id    # this is id of existing observation
    print("Existing ID:",obsPtr)
              #theObs = Observation.objects.filter( id = obsPtr)
              #print("existing obs:",theObs)
    Observation.objects.filter( id = obsPtr ).update(endDate = endDateTZ, size=obsSize)

# Register a heartbeat

#from datetime import datetime, timezone

#station_instance.last_alive = dt.now(timezone.utc)
# the station_status will update by itself when queried.
#station_instance.save()

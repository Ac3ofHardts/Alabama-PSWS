# psws_addMAG.py
# Add magnetometer observations (where upload was detected by psws_watch) to
# Observations table

import os, sys
#  admin to use Djago ORM for db updating
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'PSWS.PSWS.settings'
from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
from django.db import models
django.setup()
#from centerfrequencies.models import *
from observations.models import *
from datatypes.models import *
#import datetime

from datetime import timezone
from datetime import datetime as dt
import datetime as dz

def writeLog(theMessage):
    timestamp = dt.now(timezone.utc).isoformat()[0:19]
    f = open("/home/bengelke/Documents/watchdog.log", "a")
    f.write(timestamp + " " + theMessage + "\n")
    f.close()

# Arguments are: (1) path, (2) station_id, (3) instrument, (4) trigger

path = str (sys.argv[1])
#print("path: '" + path + "'")
station_name  = str(sys.argv[2])
#print("station: '" + station_name + "'")
instrument_name = str(sys.argv[3])
#print("instrument: '" + instrument_name + "'")
time_stamp = str(sys.argv[4])  # time stamp of the trigger

theStationQS = Station.objects.filter(station_id=station_name)
#print("found station:",theStationQS)
#print("values:",theStationQS.values())
#print("id by item:",theStationQS.values()[0]["id"])
station_id = theStationQS.values()[0]["id"]
station_instance = Station.objects.get(station_id = station_name) # Look up ID of this Station
# Now check that the instrument name given is assigned to this Station
# In addition, we check if we are given the instrument name or ID
if instrument_name.isdigit():
    if Instrument.objects.filter(id=int(instrument_name)).exists():
        # We've been given the instrument id, so pull data using ID
        theInstrumentQS = Instrument.objects.filter(id=int(instrument_name), station_id=station_id)
else:
    # Given instrument name, so pull data using name
    theInstrumentQS = Instrument.objects.filter(instrument=instrument_name, station_id=station_id)

try:
    instrument_id = theInstrumentQS.values()[0]["id"]
except IndexError as e:
    # the instrument given is not assigned to this station
    writeLog("ERROR. User specified " + station_name + " & " + instrument_name + "; no database match")
    exit()

print("found instrument:",theInstrumentQS)
#a = input()
print("getting directory list from path:",path)
fileList = os.listdir(path)  # get list of files in the supplied path
print("files to be processed:",len(fileList))
for thisfile in fileList:
    if thisfile[0] == ".":
        continue  # ignore any hidden files
    #print("filename:",thisfile)
    startDate = thisfile[3:19] # filename must be of the form OBSYYYY-MM-DDTHH:SS.zip
#    print("startdate:",startDate)
    obsSize = os.path.getsize(os.path.join(path, thisfile))
#    print("file size:",obsSize)
    startDateTZ = dt.strptime(startDate, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
# temporary
    endDateTZ = dt.strptime(time_stamp, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
#    print("startdate:", str(startDateTZ))
   # a=input()
    # Look to see if this observation is already in the database  (for this station and user)
    thisObsQS = Observation.objects.filter(fileName = thisfile, station_id=station_id, instrument_id=instrument_id)
 # this size update should be done only if mag data file has today's date! 
    today = dt.utcnow().date()
    try:
        observationID = thisObsQS.values()[0]["id"]  # try to extract the id (can also be gotten by: obsPtr=thisObsQS[0].id
        #today = dt.utcnow().date()
 #       print("found observation id ",str(observationID))
 #       print("obs date:", str(startDateTZ.date())," today:",str(today))
        if startDateTZ.date() == today:
  #          print("this observation is from today, will update time and size")
           # a=input()

            Observation.objects.filter(id=observationID).update(size=obsSize, endDate=endDateTZ)

#  there is a time stamp in the trigger directory that can be used to update the end date
    except IndexError as e: # this observation is not yet in the database
       if startDateTZ.date() == today:  # use previously set end time in trigger
   #       print("this observation is from today, setting end time to trigger time")
          noop = 1 
       else:  # adding historical file; set end time to end of that day
          endDateTZ = startDateTZ + dz.timedelta(hours=23,minutes=59)
        # add this observation
       theObs  = Observation(dataRate=1,size=obsSize,fileName=thisfile,path=path,  \
              startDate=startDateTZ, endDate=endDateTZ, \
              station_id = station_id, instrument_id = instrument_id )
       theObs.save()
       try:
           dataType = DataType.objects.filter(dataType='magnetometer').values('id') # not working as of 2024-01-15
           theObs.dataType.add(dataType[0]["id"])
           # DataType Fix - Anderson November 2023
           print("datatype!! = ", dataType, "  ID = ", dataType[0]["id"])
           writeLog("Add data type to MAG" )
       except Exception as ex:
           template = "An exception of type {0} occurred. Arguments:\n{1!r}"
           message = template.format(type(ex).__name__, ex.args)
           writeLog("While adding data type:" + message)
       print("saving obs")
       # a=input()
       theObs.save()

# Register a heartbeat

#from datetime import datetime, timezone

station_instance.last_alive = dt.now(timezone.utc)
# the station_status will update by itself when queried.
station_instance.save()

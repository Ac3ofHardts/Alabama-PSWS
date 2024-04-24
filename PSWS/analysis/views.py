from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponse
import pytz
from datetime import datetime, timedelta, timezone
import zipfile
from stations.models import Station
from observations.models import Observation
from instruments.models import Instrument
from instrumenttypes.models import InstrumentType
from observations.tables import ObservationTable
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from json import dumps
from statistics import mean 

#Declaring time cutoffs here since will probably change in the future
onlineCutoffHours = 24
possiblyOnlineCutoffHours = 120 #5 days

# Create your views here.

#def analysis_view(request):
#    return render(request, 'analysis.html')

# Display more detailed information about a station
def station_analysis(request, id=None):
    station = get_object_or_404(Station, id=id)

    #mag_stations = Station.objects.all()
    table = ObservationTable(Observation.objects.filter(station_id=id))
    table.paginate(page=request.GET.get("page", 1), per_page=8)
    return render(request, 'station_analysis.html',
        {'station': station, 'table': table}
            )

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

# def smooth_data(datalist):
#     left=0
#     right=60
#     if len(datalist)<right:
#         return datalist
#     newdatalist=[]
#     while right<len(datalist):  #average every 60 pts to 1pt and put in list, move window to 1pt right.
#         newdatalist.append(sum(datalist[left:right])/60)
#         left+=1
#         right+=1

#     return newdatalist


####### take the resquest from frontend to request information from database, then return the requested value########
####### data is averaged by minutes data #######
def analysis_map(request):
    # updateStatus()
    
    # Filtering for Magnetometer stations only
    # all_stations = Station.objects.all()
    # mag_instruments = Instrument.objects.filter(instrumenttype=3)
    # mag_instruments = Instrument.objects.get(id=mag_instruments)
    # mag_stations = Station.objects.all(instrument__id__in = mag_instruments)
    mag_stations = Station.objects.filter(instrument__id__in = Instrument.objects.filter(instrumenttype=3))
    msg=''
 #   mapbox_access_token = 'pk.eyJ1IjoiYWI0ZWotMSIsImEiOiJjazB1MTRmMTAwamVlM2Jwb2pheWx2cWpmIn0.cGZbctIFT5jSgBi0jBPk3w'
    mapbox_access_token = 'pk.eyJ1Ijoicm9sbHRpZGUiLCJhIjoiY2tueXFmMXhzMGt1MTJ1cDZ4YXkzOXJ3aiJ9.1HmCO6w6W-3r7Ou2HpRaMg'
    online_stations = Station.objects.filter(station_status="Online")
    possiblyonline_stations = Station.objects.filter(station_status="PossiblyOnline")
    offline_stations = Station.objects.filter(station_status="Offline")
    datasets=None
    dataJSON=[]
    if request.method=="POST":
        datasets=[]
        # print(request.POST)
        # <QueryDict: {'csrfmiddlewaretoken': ['KPFAd72ZpMpu5uVxY6ubLA7UysPXJKNvX6I56xIoMCMRb9seizA3auUU2INuIORk'], 
        # 'start_datetime': ['2022-12-09T00:00'], 'end_datetime': ['2022-12-09T23:59'], 'station': ['3', '33']}>

        station_ids=request.POST.getlist('station')
        if len(station_ids)==0:
            msg='No stations are selected.'
            datasets=None
            return render(request, 'analysis_map.html',
            { 'mapbox_access_token' : mapbox_access_token,
                'online_stations' : online_stations,
                'mag_stations': mag_stations,
                'datasets':datasets,
                'possiblyonline_stations' : possiblyonline_stations,
                'offline_stations' : offline_stations,
                'message':msg
                } )
        elif len(station_ids)>10:
            msg='Maximum 10 stations are allowed.'
            datasets=None
            return render(request, 'analysis_map.html',
            { 'mapbox_access_token' : mapbox_access_token,
                'online_stations' : online_stations,
                'mag_stations': mag_stations,
                'datasets':datasets,
                'possiblyonline_stations' : possiblyonline_stations,
                'offline_stations' : offline_stations,
                'message':msg
                } )
    
        
        start=str(request.POST.get('start_datetime'))
        end=str(request.POST.get('end_datetime'))
       
        if start == '':# or end == '':
            messages.error(request, "Error: Blank fields")
            datasets=None
            msg='"Error: Blank fields"'
            return render(request, 'analysis_map.html',
                { 'mapbox_access_token' : mapbox_access_token,
                    'online_stations' : online_stations,
                    'mag_stations': mag_stations,
                    'datasets':datasets,
                    'possiblyonline_stations' : possiblyonline_stations,
                    'offline_stations' : offline_stations,
                    'message':msg,
                    })
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        # print(Observation.objects.all())  #all objects queryset()
        utc=pytz.UTC #the startDate in database is aware datatime, has to convert to same type
        start_converted = utc.localize(datetime.strptime(start, '%Y-%m-%dT%H:%M'))# 'start_datetime': ['2022-12-09T00:00'], '
        
        # Incrementing start day by one to find end time. This is so the user doesn't have to provide an endtime
        #end_converted = utc.localize(datetime.strptime(end, '%Y-%m-%dT%H:%M'))
        end_converted = start_converted + timedelta(days=.5)

        if (end_converted < start_converted):
            messages.error(request, "Error: End date before start date")
            datasets=None
            msg='Error: End date before start date.'
            return render(request, 'analysis_map.html',
                { 'mapbox_access_token' : mapbox_access_token,
                    'online_stations' : online_stations,
                    'mag_stations': mag_stations,
                    'datasets':datasets,
                    'possiblyonline_stations' : possiblyonline_stations,
                    'offline_stations' : offline_stations,
                    'message':msg,
                    })
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        # if (end_converted - start_converted).days > 7:
        #     messages.error(request, "You've selected " + str((end_converted - start_converted).days) + " days. Please limit to at most 7 days")
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) 

        for id in station_ids:
            ts=[]
            xs=[]
            ys=[]
            zs=[]
            name=""
            try:
                station = get_object_or_404(Station, id=int(id))
                name=station.nickname
                address=station.city+' '+station.state
                ob=Observation.objects.filter(station_id=int(id))
              # Choices are: band, centerFrequency, dataRate, dataType, endDate, fileName, id, instrument, instrument_id, path, size, startDate, station, station_id
            except:
                ob=None
            if ob!=None:
                for o in ob.all():
                    file_extension=o.fileName[-4:]
                    if (o.startDate.date()>=start_converted.date()) and (o.endDate.date()<=end_converted.date()) and file_extension=='.zip':
                        path=('/').join(o.path.split('/')[:-1])+'/'+o.fileName
                        print(path)
                        try:
                            with zipfile.ZipFile(path) as zf:
                                for file in zf.namelist():
                                    with zf.open(file) as f:
                                        try:
                                            # switch file format
                                            # line=f.readlines()[0]
                                            # print(line)
                                            # continue
                                            #case 1 b'{ "ts":"14 Nov 2022 00:00:00", "rt":16.56, "lt":29.56, "x":-44.0088, "y":0.9507, "z":-18.7339, "rx":-390, "ry":8, "rz":-166, "Tm": 47.8397 }\n'
                                            #case 2 ,x is [3] "15 Nov 2022 07:58:00", 17.62, 34.44, 3936.0, -253.3, 2800.0, 2952, -190, 2100, 4836.96948
                                            #case 3 , x is [2]'"14 Nov 2022 00:00:00", 17.81, -38.2493, -18.8440, -14.1587, -28, -14, -10, 44.9286\n' 
                                            #case 4 ['{ "ts":"22 Nov 2022 00:00:01"', ' "rt":13.44', ' "x":-38.340', ' "y":-18.920', ' "z":-13.707', ' "rx":-5751', ' "ry":-2838', ' "rz":-2056', ' "Tm": 44.89760 }\n']
                                            #case 5 [' Time: 07 Dec 2022 00:00:00', ' rTemp: 10.19', ' lTemp: 12.38', ' x: 47.307', ' y: -0.507', ' z: -14.800', ' rx: 3548', ' ry: -38', ' rz: -1110\n']
                                            # switch format issue 4  float error ['"22 Nov 2022 16:59:45"', ' 13.75', ' -93129.3', ' 0.0', ' 0.0', ' -139694', ' 0', ' 0', ' 93129.33333\n']
                                            data=f.readlines()
                                            if len(data)>0:
                                                totalcount=0
                                                check_case=0
                                                if str(data[0],'UTF-8')[0]=='{' and len(str(data[0],'UTF-8').split(','))==10:
                                                    check_case=1
                                                elif str(data[0],'UTF-8')[0]=='{' and len(str(data[0],'UTF-8').split(','))==9:
                                                    check_case=4
                                                elif len(str(data[0],'UTF-8').split(','))==9 and str(data[0],'UTF-8')[1]=='T':
                                                    check_case=5
                                                elif len(str(data[0],'UTF-8').split(','))==10:
                                                    check_case=2
                                                elif len(str(data[0],'UTF-8').split(','))==9:
                                                    check_case=3
                                                linecount=xx=yy=zz=0
                                                for d in data:  #sum and take avg of minutes data
                                                    totalcount+=1
                                                    d=str(d,'UTF-8')
                                                    ds=d.split(',')
                                                    linecount+=1
                                                    if check_case==1:
                                                        t=ds[0][8:-4]
                                                        realtime=utc.localize(datetime.strptime(t, '%d %b %Y %H:%M'))
                                                        if realtime>end_converted:
                                                            break
                                                        xx+=float(ds[3][5:])
                                                        yy+=float(ds[4][5:])
                                                        zz+=float(ds[5][5:])
                                                    
                                                    elif check_case==4:
                                                        t=ds[0][8:-4]
                                                        realtime=utc.localize(datetime.strptime(t, '%d %b %Y %H:%M'))
                                                        if realtime>end_converted:
                                                            break
                                                        xx+=float(ds[2][5:])
                                                        yy+=float(ds[3][5:])
                                                        zz+=float(ds[4][5:])
                                                        
                                                    elif check_case==5:
                                                        t=ds[0][7:-4]
                                                        print('case 5',t)
                                                        realtime=utc.localize(datetime.strptime(t, '%d %b %Y %H:%M'))
                                                        if realtime>end_converted:
                                                            break
                                                        xx+=float(ds[3][4:])
                                                        yy+=float(ds[3][4:])
                                                        zz+=float(ds[3][4:])
                                                      
                                                    elif check_case==3:
                                                        t=ds[0][1:-4]
                                                        realtime=utc.localize(datetime.strptime(t, '%d %b %Y %H:%M'))
                                                        if realtime>end_converted:
                                                            break
                                                        xx+=float(ds[3][1:])
                                                        yy+=float(ds[4][1:])
                                                        zz+=float(ds[5][1:])
                                                 
                                                    elif check_case==2 :
                                                        t=ds[0][1:-4]
                                                        realtime=utc.localize(datetime.strptime(t, '%d %b %Y %H:%M'))
                                                        if realtime>end_converted:
                                                            break
                                                        xx+=float(ds[3][1:])
                                                        yy+=float(ds[4][1:])
                                                        zz+=float(ds[5][1:])
                                                     
                                                    if linecount==60: #take only averaged every 60s data
                                                        # selected_time=['00:00','06:00','12:00','18:00','23:59'] #only show selected time
                                                        t=t[-5:]
                                                        # if t in selected_time:
                                                        #     ts.append(t)
                                                        # else:
                                                        #     ts.append('0')
                                                        # t=datetime.strptime(t, '%d %b %Y %H:%M')
                                                        ts.append(t)
                                                        xs.append(xx/60)
                                                        ys.append(yy/60)
                                                        zs.append(zz/60)
                                                        xx=yy=zz=linecount=0
                                                    elif len(data)-totalcount==0 : #tail condition, if the data reaches the end but not 60
                                                        # if t in selected_time:
                                                        #     ts.append(t)
                                                        # else:
                                                        #     ts.append('0')
                                                        t=t[-5:]
                                                        ts.append(t)
                                                        xs.append(xx/linecount)
                                                        ys.append(yy/linecount)
                                                        zs.append(zz/linecount)
                                                        xx=yy=zz=linecount=0 
                                               
                                        except Exception as e: 
                                            print(ds)
                                            print(check_case)
                                            print(e)
                                            print(str(data[0],'UTF-8')[0])
                        except Exception as e: 
                            print(e)
            else:
                print("not found!")
            print(len(xs))

            print(id)
            print(name)
            if len(xs)>1:
                # print(xs[0:20])
                if (abs(xs[0])/10<10):
                    xs=[x*1000 for x in xs]
                    ys=[y*1000 for y in ys]
                    zs=[z*1000 for z in zs]
                # print(xs[0:20])
                x_m=mean(xs)
                y_m=mean(ys)
                z_m=mean(zs)
                # print(x_m)
                xs=[x -x_m for x in xs]
                ys=[y - y_m for y in ys]
                zs=[z- z_m for z in zs]
                # print(xs[0:20])
                # 43: KD1LE Node 0000043  -no data
                # 33: JJmp ok
                # 32: Mag_kv0s4  ok
                # 30: Grape32 has formating issue, no -zip 
                # 28: W2NAF  ok
                # 4: Grape N000019    -no data
                # 3: N000003_A  ok
                if id=='28': 
                    xxs=[z for z in zs]
                    zs=xs
                    xs=xxs
                if id=='33':
                    temp=xs
                    xs=[z*-1 for z in zs]
                    zs=temp
                if id=='4':
                    xs=[x*0.01 for x in xs]
                    ys=[y*0.01 for y in ys]
                    zs=[z*0.01 for z in zs]
                if id=='3':
                    xs=[-10*x for x in xs]
                    ys=[-10*y for y in ys]
                    zs=[10*z for z in zs]
                    temp=xs
                    xs=zs
                    zs=temp
                if id=='32':
                    ys=[y*-1 for y in ys]
                    temp=xs
                    xs=[z*-1 for z in zs]
                    zs=temp
            datasets.append({'station_id': id, 'station_name':name,'station_address':address,'ts':ts,'xs':xs,'ys':ys,'zs':zs}) 
        
        return render(request, 'analysis_map.html',
            { 'mapbox_access_token' : mapbox_access_token,
                'online_stations' : online_stations,
                'mag_stations': mag_stations,
                'datasets':datasets,
                'start': start.replace('T',' '),
                'end':end.replace('T',' '),
                'possiblyonline_stations' : possiblyonline_stations,
                'offline_stations' : offline_stations,
                'message':msg,
                } )       
        # # TODO: Add try catch here to replace blank if statement above
    
    return render(request, 'analysis_map.html',
      { 'mapbox_access_token' : mapbox_access_token,
          'online_stations' : online_stations,
          'mag_stations': mag_stations,
          'datasets':datasets,
          'start': '',
          'end':'',
          'possiblyonline_stations' : possiblyonline_stations,
          'offline_stations' : offline_stations,
          'message':msg,
        } )
    
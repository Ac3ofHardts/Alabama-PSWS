'''
Test implementation of FastAPI download API
Abandoned in favor of DRF for ease of integration with Django, but kept for reference
Main concerns were around authentication since FastAPI does not have built-in support for Django authentication

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PSWS.settings")
import django
django.setup()

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import tempfile
import zipfile
from stations.models import Station
from observations.models import Observation
import shutil

from django.contrib.auth import authenticate, login

app = FastAPI(title="Observations REST API")

@app.get("/", response_class=JSONResponse)
def read_root():
    return {"message": "Welcome to the Observations REST API"}

@app.get("/observations/download", response_class=FileResponse)
def download_observation(
    request: Request,
    station_id: str = Query(..., description="ID of the station"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    username: str = Query(..., description="Username for authentication"),
    password: str = Query(..., description="Password for authentication"),
):
    """
    Authenticated REST endpoint to download observation data.
    Example:
      curl "http://127.0.0.1:8000/observations/download?station_id=S000028&start_date=2022-12-09&end_date=2022-12-11&username=testuser&password=testpassword"
    """
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must be in YYYY-MM-DD format")
        
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    if not Station.objects.filter(station_id=station_id).exists():
        raise HTTPException(status_code=404, detail="Station not found")
    
    observations_in_range = Observation.objects.filter(
        station__station_id=station_id,
        startDate__gte=start_dt,
        endDate__lte=end_dt
    )
    
    if not observations_in_range.exists():
        raise HTTPException(status_code=404, detail="Observation data not found")

    observations = list(observations_in_range.all())

    # if multiple observation files are found zip them together
    if len(observations) > 1:
        temp_dir = tempfile.gettempdir()
        zip_filename = f"observation_{station_id}_{start_date}_{end_date}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for o in observations:
                    file_extension = o.fileName[-4:]
                    # ensure the file is a .zip file and is within date range
                    if (o.startDate.date() >= start_dt.date() and
                        o.endDate.date() <= end_dt.date() and 
                        file_extension == '.zip'):
                        file_path = '/'.join(o.path.split('/')[:-1]) + '/' + o.fileName
                        if not os.path.exists(file_path):
                            continue
                        zipf.write(file_path, arcname=o.fileName)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate zip file: {str(e)}")
        return FileResponse(path=zip_path, media_type="application/zip", filename=zip_filename)
    else:
        # if only one file is available return it directly
        o = observations[0]
        file_extension = o.fileName[-4:]
        if (o.startDate.date() >= start_dt.date() and
            o.endDate.date() <= end_dt.date() and 
            file_extension == '.zip'):
            file_path = '/'.join(o.path.split('/')[:-1]) + '/' + o.fileName
        else:
            raise HTTPException(status_code=404, detail="Observation file not found")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Observation file not found")
        return FileResponse(path=file_path, media_type="application/zip", filename=o.fileName)
'''
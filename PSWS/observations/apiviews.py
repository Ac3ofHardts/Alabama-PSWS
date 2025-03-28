from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import FileResponse
from datetime import datetime
import tempfile, os, zipfile

from stations.models import Station
from observations.models import Observation

class ObservationDownloadAPIView(APIView):
    authentication_classes = [BasicAuthentication]  # uses Django's basic auth
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        '''
        Curl Usage: curl -u username -o output.zip "http://pswsnetwork.caps.ua.edu/observations/downloadapi/?station_id=XXXXXXX&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"
        Wget Usage: wget --http-user=username --http-password=password -O output.zip "http://pswsnetwork.caps.ua.edu/observations/downloadapi/?station_id=XXXXXXX&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"
        '''
        
        station_id = request.query_params.get("station_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not (station_id and start_date and end_date):
            return Response({"detail": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"detail": "Dates must be in YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)

        if end_dt < start_dt:
            return Response({"detail": "End date must be after start date"}, status=status.HTTP_400_BAD_REQUEST)

        if not Station.objects.filter(station_id=station_id).exists():
            return Response({"detail": "Station not found"}, status=status.HTTP_404_NOT_FOUND)

        observations_in_range = Observation.objects.filter(
            station__station_id=station_id,
            startDate__gte=start_dt,
            endDate__lte=end_dt
        )

        if not observations_in_range.exists():
            return Response({"detail": "Observation data not found."}, status=status.HTTP_404_NOT_FOUND)

        observations = list(observations_in_range.all())

        # multiple observation files requested, zip them together
        if len(observations) > 1:
            temp_dir = tempfile.gettempdir()
            zip_filename = f"observation_{station_id}_{start_date}_{end_date}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            try:
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for obs in observations:
                        file_extension = obs.fileName[-4:]
                        if (obs.startDate.date() >= start_dt.date() and
                            obs.endDate.date() <= end_dt.date() and file_extension == '.zip'):
                            file_path = '/'.join(obs.path.split('/')[:-1]) + '/' + obs.fileName
                            #print(file_path)
                            if os.path.exists(file_path):
                                zipf.write(file_path, arcname=obs.fileName)
            except Exception as e:
                return Response({"detail": f"Failed to generate zip file: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return FileResponse(open(zip_path, 'rb'),
                                as_attachment=True,
                                filename=zip_filename,
                                content_type="application/zip")

        # single file observation file requested, return directly
        else:
            o = observations[0]
            file_extension = o.fileName[-4:]
            if (o.startDate.date() >= start_dt.date() and o.endDate.date() <= end_dt.date() and file_extension == '.zip'):
                file_path = ('/').join(o.path.split('/')[:-1]) + '/' + o.fileName
                # TEST CASE - replace developer with rocky linux username
                # file_path = "/home/developer/S000028/magData/" + o.fileName
                # print(file_path)
            else:
                return Response({"detail": "Observation file not found."},
                                status=status.HTTP_404_NOT_FOUND)
            if not os.path.exists(file_path):
                return Response({"detail": "Observation file not found."},
                                status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(file_path, 'rb'),
                                as_attachment=True,
                                filename=o.fileName,
                                content_type="application/zip")
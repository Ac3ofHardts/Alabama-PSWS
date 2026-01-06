from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework import status
from django.http import FileResponse
from datetime import datetime
import tempfile, os, zipfile
import logging
from logging.handlers import RotatingFileHandler

from stations.models import Station
from observations.models import Observation

# Configure dedicated logger for API
api_logger = logging.getLogger('observations_api')
api_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = '/home/developer/Alabama-PSWS/PSWS/logs'
os.makedirs(log_dir, exist_ok=True)

# Create rotating file handler (max 10MB per file, keep 5 backup files)
log_file = os.path.join(log_dir, 'observations_api.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# Create detailed formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handler to logger
if not api_logger.handlers:
    api_logger.addHandler(file_handler)

class ObservationDownloadAPIView(APIView):
    throttle_classes = [AnonRateThrottle]
    
    # Size threshold for multiple file downloads (in bytes)
    MAX_MULTI_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

    def get(self, request, format=None):
        '''
        Download observations API endpoint with filtering capabilities.
        
        AUTHENTICATION: No authentication required - publicly accessible with rate limiting
        
        REQUIRED PARAMETERS:
        - start_date: YYYY-MM-DD format (e.g. "2024-01-01")
        - end_date: YYYY-MM-DD format (e.g. "2024-12-31")
        
        LOCATION FILTERING (choose one):
        - station_id: Specific station identifier (e.g. "S000028")
        OR
        - lat_min, lat_max, lon_min, lon_max: Geographic bounding box
        
        OPTIONAL FILTERS:
        - instrument_id: Filter by specific instrument (integer)
        - frequency: Filter by center frequency in MHz (decimal)
        
        EXAMPLE CURL COMMANDS:
        
        1. Download by station ID:
        curl -o output.zip \
        "https://pswsnetwork.eng.ua.edu/observations/downloadapi/?station_id=S000028&start_date=2024-01-01&end_date=2024-01-31"
        
        2. Download by geographic region (Alabama):
        curl -o output.zip \
        "https://pswsnetwork.eng.ua.edu/observations/downloadapi/?lat_min=32.0&lat_max=35.0&lon_min=-88.0&lon_max=-84.0&start_date=2024-01-01&end_date=2024-01-31"
        
        3. Download with frequency filter:
        curl -o output.zip \
        "https://pswsnetwork.eng.ua.edu/observations/downloadapi/?station_id=S000028&frequency=10&start_date=2024-01-01&end_date=2024-01-31"

        4. Download with instrument filter:
        curl -o output.zip \
        "https://pswsnetwork.eng.ua.edu/observations/downloadapi/?station_id=S000028&instrument_id=1&start_date=2024-01-01&end_date=2024-01-31"

        WGET EXAMPLES:
        
        wget -O output.zip \
        "https://pswsnetwork.eng.ua.edu/observations/downloadapi/?station_id=S000028&start_date=2024-01-01&end_date=2024-01-31"

        RESPONSE:
        - Single file: Returns the observation file directly
        - Multiple files: Returns a ZIP archive containing all matching observations
        - No matches: HTTP 404 with error message
        - Invalid parameters: HTTP 400 with error details
        '''
        # Log incoming request
        api_logger.info("="*80)
        api_logger.info("NEW API REQUEST RECEIVED")
        api_logger.info(f"Client IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        api_logger.info(f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
        api_logger.info(f"Query Parameters: {dict(request.query_params)}")
        
        # REQUIRED PARAMETERS: Extract and validate date range
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # LOCATION PARAMETERS: Extract station ID or geographic coordinates
        station_id = request.query_params.get("station_id")  # Single station filter
        
        # Geographic bounding box coordinates (all four required for geo filtering)
        lat_min = request.query_params.get("lat_min")
        lat_max = request.query_params.get("lat_max") 
        lon_min = request.query_params.get("lon_min")
        lon_max = request.query_params.get("lon_max")

        # OPTIONAL FILTER PARAMETERS
        instrument_id = request.query_params.get("instrument_id")
        frequency = request.query_params.get("frequency")

        api_logger.debug(f"Extracted parameters - start_date: {start_date}, end_date: {end_date}, "
                        f"station_id: {station_id}, lat_min: {lat_min}, lat_max: {lat_max}, "
                        f"lon_min: {lon_min}, lon_max: {lon_max}, instrument_id: {instrument_id}, "
                        f"frequency: {frequency}")

        # VALIDATION: Check required date parameters
        if not (start_date and end_date):
            api_logger.warning("VALIDATION FAILED: Missing start_date or end_date parameters")
            return Response({"detail": "Missing start_date or end_date parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # VALIDATION: Parse and validate date format (YYYY-MM-DD)
        # Example valid dates: "2024-01-01", "2024-12-31"
        # Example invalid dates: "01/01/2024", "2024-1-1", "24-01-01"
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            api_logger.info(f"Date parsing successful - start_dt: {start_dt}, end_dt: {end_dt}")
        except ValueError as e:
            api_logger.warning(f"VALIDATION FAILED: Invalid date format - {e}")
            return Response({"detail": "Dates must be in YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)

        # VALIDATION: Ensure logical date range
        if end_dt < start_dt:
            api_logger.warning(f"VALIDATION FAILED: End date {end_dt} is before start date {start_dt}")
            return Response({"detail": "End date must be after start date"}, status=status.HTTP_400_BAD_REQUEST)

        # INITIAL QUERY: Filter observations by date range
        # This filters on the observation's start and end dates
        api_logger.info(f"Querying observations between {start_dt.date()} and {end_dt.date()}")
        observations_in_range = Observation.objects.filter(
            startDate__gte=start_dt,
            endDate__lte=end_dt
        )
        api_logger.debug(f"Initial date range query returned {observations_in_range.count()} observations")

        # VALIDATION: Ensure mutual exclusivity between station_id and lat/lon filtering
        # This prevents conflicting filter criteria that could lead to unexpected results
        if station_id and (lat_min or lat_max or lon_min or lon_max):
            api_logger.warning("VALIDATION FAILED: Both station_id and lat/lon parameters provided")
            return Response({"detail": "Invalid parameters: must choose either station_id or latitude and longitude range"})

        # STATION FILTERING: Filter by specific station ID (case-insensitive)
        # Example test case: station_id="S000028" should match station with ID "s000028" or "S000028"
        if station_id:
            api_logger.info(f"Applying station filter: {station_id}")
            observations_in_range = observations_in_range.filter(
                station__station_id__iexact=station_id
            )
            api_logger.debug(f"After station filter: {observations_in_range.count()} observations")
            
            # Check if station exists
            if not observations_in_range.exists():
                # Verify if the station exists at all
                station_exists = Station.objects.filter(station_id__iexact=station_id).exists()
                if not station_exists:
                    api_logger.warning(f"Station '{station_id}' not found in database")
                else:
                    api_logger.warning(f"Station '{station_id}' exists but has no observations in date range")
        # GEOGRAPHIC FILTERING: Filter by latitude/longitude bounding box
        # All four coordinates must be provided for geographic filtering
        # Example test cases:
        # - lat_min=32.0, lat_max=34.0, lon_min=-87.0, lon_max=-85.0 (Alabama region)
        # - lat_min=25.0, lat_max=49.0, lon_min=-125.0, lon_max=-66.0 (Continental US)
        # - lat_min=40.0, lat_max=41.0, lon_min=-74.0, lon_max=-73.0 (NYC area)
        elif lat_min and lat_max and lon_min and lon_max:
            api_logger.info(f"Applying geographic filter: lat [{lat_min}, {lat_max}], lon [{lon_min}, {lon_max}]")
            try:
                # Convert to float to ensure proper numeric comparison
                lat_min_f = float(lat_min)
                lat_max_f = float(lat_max)
                lon_min_f = float(lon_min)
                lon_max_f = float(lon_max)
                
                api_logger.debug(f"Parsed geographic coordinates: lat [{lat_min_f}, {lat_max_f}], lon [{lon_min_f}, {lon_max_f}]")
                
                # VALIDATION: Check coordinate bounds and logical consistency
                # Latitude must be between -90 and 90 degrees
                if not (-90 <= lat_min_f <= 90 and -90 <= lat_max_f <= 90):
                    api_logger.warning(f"VALIDATION FAILED: Latitude values out of bounds - lat_min: {lat_min_f}, lat_max: {lat_max_f}")
                    return Response({"detail": "Latitude values must be between -90 and 90 degrees"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Longitude must be between -180 and 180 degrees
                if not (-180 <= lon_min_f <= 180 and -180 <= lon_max_f <= 180):
                    api_logger.warning(f"VALIDATION FAILED: Longitude values out of bounds - lon_min: {lon_min_f}, lon_max: {lon_max_f}")
                    return Response({"detail": "Longitude values must be between -180 and 180 degrees"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Min values must be less than or equal to max values
                if lat_min_f > lat_max_f:
                    api_logger.warning(f"VALIDATION FAILED: lat_min ({lat_min_f}) > lat_max ({lat_max_f})")
                    return Response({"detail": "lat_min must be less than or equal to lat_max"}, status=status.HTTP_400_BAD_REQUEST)
                
                if lon_min_f > lon_max_f:
                    api_logger.warning(f"VALIDATION FAILED: lon_min ({lon_min_f}) > lon_max ({lon_max_f})")
                    return Response({"detail": "lon_min must be less than or equal to lon_max"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Apply geographic filter using validated coordinates
                observations_in_range = observations_in_range.filter(
                    station__latitude__gte=lat_min_f,
                    station__latitude__lte=lat_max_f,
                    station__longitude__gte=lon_min_f,
                    station__longitude__lte=lon_max_f
                )
                api_logger.debug(f"After geographic filter: {observations_in_range.count()} observations")
            except (ValueError, TypeError) as e:
                api_logger.warning(f"VALIDATION FAILED: Invalid lat/lon values - {e}")
                return Response({"detail": "Latitude and longitude values must be valid numbers"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            api_logger.warning("VALIDATION FAILED: No valid location filter provided (neither station_id nor complete lat/lon range)")
            return Response({"detail": "Invalid parameters: must include either station_id or latitude and longitude range"}, status=status.HTTP_400_BAD_REQUEST)
        
        # INSTRUMENT FILTERING: Filter by specific instrument ID if provided
        # Example test case: instrument_id=1 should return only observations from instrument with ID 1
        if instrument_id:
            api_logger.info(f"Applying instrument filter: {instrument_id}")
            try:
                instrument_id_int = int(instrument_id)
                observations_in_range = observations_in_range.filter(
                    instrument__id=instrument_id_int
                )
                api_logger.debug(f"After instrument filter: {observations_in_range.count()} observations")
            except (ValueError, TypeError) as e:
                api_logger.warning(f"VALIDATION FAILED: Invalid instrument_id - {e}")
                return Response({"detail": "instrument_id must be a valid integer"}, status=status.HTTP_400_BAD_REQUEST)
        
        # FREQUENCY FILTERING: Filter by center frequency if provided
        # Note: This filters on the centerFrequency field value in MHz
        if frequency:
            api_logger.info(f"Applying frequency filter: {frequency} MHz")
            try:
                frequency_decimal = float(frequency)
                # Validate frequency range (assuming reasonable RF frequencies in MHz)
                if frequency_decimal <= 0 or frequency_decimal > 300000:  # 0 Hz to 300 GHz
                    api_logger.warning(f"VALIDATION FAILED: Frequency out of range - {frequency_decimal} MHz")
                    return Response({"detail": "Frequency must be a positive value in MHz (0-300000)"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Filter observations by center frequency
                # Note: The relationship is observations -> centerFrequency (ManyToMany) -> centerFrequency field
                observations_in_range = observations_in_range.filter(
                    centerFrequency__centerFrequency=frequency_decimal
                )
                api_logger.debug(f"After frequency filter: {observations_in_range.count()} observations")
            except (ValueError, TypeError) as e:
                api_logger.warning(f"VALIDATION FAILED: Invalid frequency value - {e}")
                return Response({"detail": "Frequency must be a valid decimal number in MHz"}, status=status.HTTP_400_BAD_REQUEST)

        # CHECK RESULTS: Verify that observations were found
        if not observations_in_range.exists():
            api_logger.warning("NO OBSERVATIONS FOUND matching the specified criteria")
            return Response({"detail": "Observation data not found."}, status=status.HTTP_404_NOT_FOUND)

        # RETRIEVE MATCHING OBSERVATIONS
        observations = list(observations_in_range.all())

        api_logger.info(f"FOUND {len(observations)} observations matching criteria")
        print(f"Found {len(observations)} observations matching criteria")
        for i, obs in enumerate(observations):
            log_msg = f"  Observation {i+1}: {obs.fileName} | Path: {obs.path} | Start: {obs.startDate.date()} | End: {obs.endDate.date()}"
            api_logger.debug(log_msg)
            print(log_msg)

        # SIZE VALIDATION: Check total size for multiple files
        if len(observations) > 1:
            api_logger.info(f"Multiple files detected ({len(observations)}), checking total size...")
            total_size = 0
            existing_files_count = 0
            
            print(f"Checking total size (threshold: {self.MAX_MULTI_FILE_SIZE / (1024*1024):.0f} MB)...")
            
            for obs in observations:
                # Use database size if available, otherwise check file on disk
                file_size = 0
                
                if hasattr(obs, 'size') and obs.size:
                    file_size = obs.size
                    log_msg = f"  {obs.fileName}: {file_size / (1024*1024):.2f} MB (from database)"
                    api_logger.debug(log_msg)
                    print(log_msg)
                else:
                    # Construct file path to check on disk
                    file_path = '/'.join(obs.path.split('/')[:-1]) + '/' + obs.fileName
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        log_msg = f"  {obs.fileName}: {file_size / (1024*1024):.2f} MB (from disk)"
                        api_logger.debug(log_msg)
                        print(log_msg)
                    else:
                        log_msg = f"  {obs.fileName}: File not found at {file_path}, skipping from size calculation"
                        api_logger.warning(log_msg)
                        print(log_msg)
                        continue
                
                total_size += file_size
                existing_files_count += 1
            
            log_msg = f"Total size of {existing_files_count} existing files: {total_size / (1024*1024):.2f} MB"
            api_logger.info(log_msg)
            print(log_msg)
            
            # Check if total size exceeds threshold
            if total_size > self.MAX_MULTI_FILE_SIZE:
                api_logger.warning(f"SIZE LIMIT EXCEEDED: {total_size / (1024*1024):.2f} MB > {self.MAX_MULTI_FILE_SIZE / (1024*1024):.0f} MB")
                return Response({
                    "detail": "Request exceeds maximum file size limit for multiple file downloads.",
                    "error_info": {
                        "requested_size_mb": round(total_size / (1024*1024), 2),
                        "threshold_mb": round(self.MAX_MULTI_FILE_SIZE / (1024*1024), 0),
                        "files_count": existing_files_count,
                        "suggestion": "Please use a smaller date range or download individual files."
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        # MULTIPLE FILES: Create ZIP archive when multiple observations found
        if len(observations) > 1:
            api_logger.info("Creating ZIP archive for multiple files")
            temp_dir = tempfile.gettempdir()
            # Create descriptive filename based on search criteria
            if station_id:
                zip_filename = f"observations_{station_id}_{start_date}_{end_date}.zip"
            else:
                zip_filename = f"observations_region_{start_date}_{end_date}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            log_msg = f"Creating ZIP archive: {zip_path}"
            api_logger.info(log_msg)
            print(log_msg)
            
            files_added = 0
            files_processed = 0
            
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for obs in observations:
                        files_processed += 1
                        log_msg = f"Processing observation {files_processed}/{len(observations)}: {obs.fileName}"
                        api_logger.debug(log_msg)
                        print(log_msg)
                        
                        # VALIDATION: Only process ZIP files within date range # Removed since some files may not be .zip?
                        #file_extension = obs.fileName[-4:]
                        #if file_extension == '.zip':
                            
                        # CONSTRUCT FILE PATH: Build full path to observation file
                        file_path = '/'.join(obs.path.split('/')[:-1]) + '/' + obs.fileName
                        # TEST CASE - developer is linux username
                        #file_path = "/home/developer/S000028/magData/" + obs.fileName
                        log_msg = f"  File path: {file_path}"
                        api_logger.debug(log_msg)
                        print(log_msg)
                            
                        # VALIDATION: Check file exists before adding to ZIP
                        if os.path.exists(file_path):
                            try:
                                zipf.write(file_path, arcname=obs.fileName)
                                files_added += 1
                                log_msg = f"  ✓ Successfully added to ZIP"
                                api_logger.debug(log_msg)
                                print(log_msg)
                            except Exception as add_error:
                                log_msg = f"  ✗ Error adding file to ZIP: {add_error}"
                                api_logger.error(log_msg)
                                print(log_msg)
                        else:
                            log_msg = f"  ✗ File not found at path"
                            api_logger.warning(log_msg)
                            print(log_msg)
                        #else:
                        #    print(f"  ✗ File skipped (invalid extension or date range)")
                            
            except Exception as e:
                log_msg = f"CRITICAL ERROR creating ZIP file: {str(e)}"
                api_logger.error(log_msg, exc_info=True)
                print(log_msg)
                return Response({"detail": f"Failed to generate zip file: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            log_msg = f"ZIP creation completed: {files_added}/{files_processed} files added to archive"
            api_logger.info(log_msg)
            print(log_msg)
            
            # Check if any files were actually added
            if files_added == 0:
                api_logger.warning("NO FILES ADDED to ZIP archive - all files missing from filesystem")
                return Response({"detail": "No valid observation files found to include in archive"},
                                status=status.HTTP_404_NOT_FOUND)

            # RETURN ZIP FILE: Send ZIP archive as download with custom headers
            api_logger.info(f"Successfully returning ZIP archive with {files_added} files")
            response = FileResponse(open(zip_path, 'rb'),
                                as_attachment=True,
                                filename=zip_filename,
                                content_type="application/zip")
            
            # Add custom headers visible to user
            response['X-Files-Discovered'] = str(len(observations))
            response['X-Files-Processed'] = str(files_processed)
            response['X-Files-Added'] = str(files_added)
            response['X-Archive-Type'] = 'multiple-files'
            
            api_logger.info("Request completed successfully - ZIP file sent")
            api_logger.info("="*80)
            return response

        # SINGLE FILE: Return observation file directly
        else:
            api_logger.info("Single file response - processing")
            obs = observations[0]
            #file_extension = obs.fileName[-4:]
            
            # VALIDATION: Check file is within date range and is a ZIP file # Removed since some files may not be .zip?
            #if not file_extension == '.zip':
            #    return Response({"detail": "Observation file not found or invalid."},
            #                    status=status.HTTP_404_NOT_FOUND)
            
            # CONSTRUCT FILE PATH: Build full path to observation file
            file_path = '/'.join(obs.path.split('/')[:-1]) + '/' + obs.fileName
            # TEST CASE - developer is linux username
            #file_path = "/home/developer/S000028/magData/" + obs.fileName
            log_msg = f"Serving single file: {file_path}"
            api_logger.info(log_msg)
            print(log_msg)
            
            # VALIDATION: Verify file exists on filesystem
            if not os.path.exists(file_path):
                api_logger.error(f"FILE NOT FOUND on filesystem: {file_path}")
                return Response({"detail": "Observation file not found on filesystem."},
                                status=status.HTTP_404_NOT_FOUND)
            
            # RETURN SINGLE FILE: Send observation file as download with custom headers
            api_logger.info(f"Successfully returning single file: {obs.fileName}")
            response = FileResponse(open(file_path, 'rb'),
                                as_attachment=True,
                                filename=obs.fileName,
                                content_type="application/zip")
            
            # Add custom headers visible to user
            response['X-Files-Discovered'] = '1'
            response['X-Files-Processed'] = '1'
            response['X-Files-Added'] = '1'
            response['X-Archive-Type'] = 'single-file'
            
            api_logger.info("Request completed successfully - single file sent")
            api_logger.info("="*80)
            return response
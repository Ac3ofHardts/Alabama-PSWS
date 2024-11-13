from django.db import models
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from accounts.models import Profile
from accounts.tables import UserTable
from stations.models import Station

from django.utils import timezone
import os
import secrets
import string


def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


class Command(BaseCommand):
    help = "Create a Profile and associated Station for a user, set up a directory, and output details to a text file"

    def add_arguments(self, parser):
        # User/Profile arguments
        parser.add_argument('--username', type=str, required=True, help="Username for the user")
        parser.add_argument('--password', type=str, required=True, help="Password for the user")
        parser.add_argument('--email', type=str, required=True, help="Email for the user")

        # Make station_id a required argument
        parser.add_argument('--station_id', type=str, required=True, help="Station ID")
        
        # Station arguments
        parser.add_argument('--nickname', type=str, required=True, help="Station nickname")
        parser.add_argument('--latitude', type=float, help="Latitude of the station")
        parser.add_argument('--longitude', type=float, help="Longitude of the station")
        parser.add_argument('--grid', type=str, help="Grid code")
        parser.add_argument('--elevation', type=float, help="Elevation of the station")
        parser.add_argument('--antenna_1', type=str, help="Primary antenna type")
        parser.add_argument('--antenna_2', type=str, help="Secondary antenna type")
        parser.add_argument('--street_address', type=str, help="Street address of the station")
        parser.add_argument('--city', type=str, help="City where the station is located")
        parser.add_argument('--state', type=str, help="State where the station is located")
        parser.add_argument('--postal_code', type=str, help="Postal code of the station")
        parser.add_argument('--phone_number', type=str, help="Phone number for the station")

    def handle(self, *args, **kwargs):
        # Validate that station_id is exactly 7 characters
        station_id = kwargs['station_id']
        if len(station_id) != 7:
            self.stdout.write(self.style.ERROR("The station_id must be exactly 7 characters long. Exiting."))
            return  # Exit the program if station_id is invalid

        # Directory path for station
        station_dir = f"/home/{station_id}"

        # Check if the directory already exists and exit if it does
        if os.path.exists(station_dir):
            self.stdout.write(self.style.ERROR(f"Directory {station_dir} already exists. Exiting."))
            return  # Exit the program if directory exists

        # Extract User/Profile details
        username = kwargs['username']
        password = kwargs['password']
        email = kwargs['email']

        # Create or retrieve User
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User created for {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"User {username} already exists"))

        # Create or retrieve Profile
        profile, profile_created = Profile.objects.get_or_create(user=user, defaults={'email': email, 'signup_confirmation': True})
        if profile_created:
            self.stdout.write(self.style.SUCCESS(f"Profile created for {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"Profile for user {username} already exists"))

        station_pass = generate_random_string()

        # Extract Station details
        station_data = {
            'user': user,
            'station_id': station_id,
            'nickname': kwargs['nickname'],
            'latitude': kwargs.get('latitude'),
            'longitude': kwargs.get('longitude'),
            'grid': kwargs.get('grid'),
            'elevation': kwargs.get('elevation'),
            'antenna_1': kwargs.get('antenna_1'),
            'antenna_2': kwargs.get('antenna_2'),
            'street_address': kwargs.get('street_address'),
            'city': kwargs.get('city'),
            'state': kwargs.get('state'),
            'postal_code': kwargs.get('postal_code'),
            'phone_number': kwargs.get('phone_number'),
            'create_date': timezone.now(),
            'station_pass': station_pass
        }

        # Create Station
        station = Station.objects.create(**station_data)
        self.stdout.write(self.style.SUCCESS(f"Station '{station.nickname}' created for user {username}"))

        # Run directory creation command
        os.system(f'sudo /bin/stationcreation3 {station.station_id} {station.station_pass}')
        self.stdout.write(self.style.SUCCESS(f"Directory created for station {station.station_id}"))

        # Prepare output file content
        output_content = (
            f"User and Profile Details\n"
            f"Username: {user.username}\n"
            f"Password: {password}\n"  # Show the input password
            f"Email: {profile.email}\n"
            f"Signup Confirmation: {profile.signup_confirmation}\n\n"
            f"Station Details\n"
            f"Station ID: {station.station_id}\n"
            f"Nickname: {station.nickname}\n"
            f"Latitude: {station.latitude}\n"
            f"Longitude: {station.longitude}\n"
            f"Grid: {station.grid}\n"
            f"Elevation: {station.elevation}\n"
            f"Antenna 1: {station.antenna_1}\n"
            f"Antenna 2: {station.antenna_2}\n"
            f"Street Address: {station.street_address}\n"
            f"City: {station.city}\n"
            f"State: {station.state}\n"
            f"Postal Code: {station.postal_code}\n"
            f"Phone Number: {station.phone_number}\n"
            f"Created Date: {station.create_date}\n"
        )

	# Define the output directory and initial file path
        output_dir = "/home/user/user_creation_outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(self.style.SUCCESS(f"Created directory {output_dir}"))

        # Check if file exists and increment filename if necessary
        base_file_path = os.path.join(output_dir, f"{username}_details.txt")
        output_file_path = base_file_path
        counter = 1
        while os.path.exists(output_file_path):
            output_file_path = os.path.join(output_dir, f"{username}_details_{counter}.txt")
            counter += 1

        # Write output to the file
        with open(output_file_path, 'w') as file:
            file.write(output_content)

        self.stdout.write(self.style.SUCCESS(f"Details saved to {output_file_path}"))

from rest_framework import serializers
from stations.models import Station

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['user', 'nickname', 'station_status', 'station_id', 'last_alive']

class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['nickname', 'station_id', 'station_pass']

from django.urls import path
from . import views

urlpatterns = [
    path('stations/', views.station_list_view, name="stations"),
    path('add/', views.add_station_view, name="add_station"),
    path('update/$', views.update_station_view, name="station_update"),
    path('update/?P<id>[0-9]+)/$', views.update_station_view, name="station_update"),
    path('my_stations_list/', views.my_stations_list_view, name="my_stations_list"),
    path('station_details/$', views.station_details_view, name="station_details"),
    path('station_details/?P<id>[0-9]+)/$', views.station_details_view, name="station_details"),
]

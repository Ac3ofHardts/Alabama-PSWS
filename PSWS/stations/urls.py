from django.urls import path, re_path
from . import views
from .views import StationListView, MyStationsListView

urlpatterns = [
    #path('stations/', views.station_list_view, name="stations"),
    path('stations/', StationListView.as_view(), name="stations"),
    path('add/', views.add_station_view, name="add_station"),
    path('update/<int:id>/', views.update_station_view, name="station_update"),
    #path('my_stations_list/', views.my_stations_list_view, name="my_stations_list"),
    path('my_stations_list/', MyStationsListView.as_view(), name="my_stations_list"),
    path('station_details/<int:id>/', views.station_details_view, name="station_details"),
    ]

#url paths updated to use current django url paths instead of regular expressions

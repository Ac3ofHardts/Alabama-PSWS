from django.urls import path
from . import views

urlpatterns = [
    path('stations', views.station_list_view, name="stations"),
    path('add/', views.add_station_view, name="add_station"),
    path('update/', views.station_update_view, name="station_update"),
]

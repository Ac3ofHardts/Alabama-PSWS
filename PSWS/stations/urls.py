from django.urls import path
from . import views

urlpatterns = [
    path('stations', views.station_list_view, name="stations"),
]

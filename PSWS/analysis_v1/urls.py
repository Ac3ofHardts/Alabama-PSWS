from django.urls import path
from . import views

urlpatterns = [
        path('analysis/', views.analysis_map, name='analysis_map'),
        path('analysis/station_analysis/<int:id>/', views.station_analysis, name='station_analysis'),
        ]
   

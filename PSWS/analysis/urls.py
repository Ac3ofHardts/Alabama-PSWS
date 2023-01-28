from django.urls import path
from . import views

urlpatterns = [
        path('analysis/', views.analysis_map, name='analysis'),
        path('station_analysis/<int:id>', views.station_analysis, name='station_analysis'),
        ]
   

from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
        # path('line_plot/', views.line_plot, name='line_plot'),
        path('analysis/', views.analysis_map, name='analysis_map'),
        # path to display graphs
        path('analysis/display_graphs/', views.under_construction, name='display_graphs'),
        # do we need next anymore?
        path('analysis/station_analysis/<int:id>/', views.under_construction, name='station_analysis'),
	]
   

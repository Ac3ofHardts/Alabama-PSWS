from django.urls import path
from . import views

urlpatterns = [
        path('analysis/', views.analysis_view, name='analysis')
        ]
   

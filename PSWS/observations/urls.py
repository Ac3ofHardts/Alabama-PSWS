from django.urls import path
from . import views
from .views import ObservationListView

urlpatterns = [
        path('observation_list/', ObservationListView.as_view(), name="observation_list"),
        path('download/<int:id>/', views.download_file, name='download_file'),
        path('download/<int:id>/', views.download_range, name='download_range'),
        ]

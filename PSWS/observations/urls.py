from django.urls import path
from . import views
from .views import ObservationListView

urlpatterns = [
        path('observation_list/', ObservationListView.as_view(), name="observation_list"),
        path('download/<int:id>/', views.download_file, name='download_file'),
        path('downloadplot/<int:id>/', views.download_plot, name='download_plot'),
        path('download/<int:id>/', views.download_range, name='download_range'),
        path('range/<int:id>/', views.get_date_range, name='get_date_range'),
        path('select_download_range/<int:id>/', views.select_download_range, name='select_download_range'),
        path('download_range/<int:id>/', views.download_range, name='download_range'),
        ]

from django.urls import path
from . import views
from .views import ObservationListView

urlpatterns = [
        path('observation_list/', ObservationListView.as_view(), name="observation_list"),
        ]

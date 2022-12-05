from django.urls import path, re_path
from . import views
from .views import InstrumentListView

urlpatterns = [
        path('instruments/', views.InstrumentListView, name = "instruments"),
        path('add/', views.add_instrument_view, name="add_instrument"),
        path('add/<int:id>/', views.add_instrument_view, name = "add_instrument"),
        path('update/<int:id>/', views.update_instrument_view, name="instrument_update"),
        path('instrument_details/<int:id>/', views.instrument_details_view, name="instrument_details"),
        ]


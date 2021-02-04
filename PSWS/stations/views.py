from django.shortcuts import render
from django.contrib.auth.decorators import login_requirded

# Create your views here.

@login_required
def station_list_view(request):
    return render(request, 'stations.html')

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def analysis_view(request):
    return render(request, 'analysis.html')


from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadFileForm

# Create your views here.

@login_required
def files(request):
        return render(request, 'files.html')

def file_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upoloaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
        else:
            form = UploadFileForm()
        return render(request, 'upload.html', {'form':form})

def handle_uploaded_file(f):
    with open(

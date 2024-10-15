from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text, force_bytes
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django_tables2 import SingleTableView



from .forms import SignUpForm, EditProfileForm
from .tokens import account_activation_token
from .models import Profile
from .tables import UserTable
from stations.models import Station

import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta, timezone

#Declaring time cutoffs here since will probably change in the future
onlineCutoffHours = 24
possiblyOnlineCutoffHours = 120 #5 days
retirementCutoffHours = 504



def updateStatus():
    #Update Station status of all stations before displaying
    AliveCutoff = datetime.now(timezone.utc) - timedelta(hours=onlineCutoffHours)
    DeadCutoff = datetime.now(timezone.utc) - timedelta(hours=possiblyOnlineCutoffHours)
    RetiredCutoff = datetime.now(timezone.utc) - timedelta(hours=retirementCutoffHours)

    for instance in Station.objects.all():
        if (instance.last_alive is None):
            instance.last_alive = datetime(2000,1,1,tzinfo=timezone.utc)
        if (instance.last_alive < RetiredCutoff):
            instance.station_status = "Retired"
        elif (instance.last_alive < DeadCutoff):
            instance.station_status = "Offline"
        elif (instance.last_alive < AliveCutoff):
            instance.station_status = "PossiblyOnline"
        else:
            instance.station_status = "Online"
       # if station has never submitted an upload, they are marked inactive
       # and won't show on map
        if (instance.last_alive == datetime(2000,1,1,tzinfo=timezone.utc)):
            instance.station_status = "Inactive"
        instance.save()

def home(request):
    updateStatus()
 #   mapbox_access_token = 'pk.eyJ1IjoiYWI0ZWotMSIsImEiOiJjazB1MTRmMTAwamVlM2Jwb2pheWx2cWpmIn0.cGZbctIFT5jSgBi0jBPk3w'
    mapbox_access_token = 'pk.eyJ1Ijoicm9sbHRpZGUiLCJhIjoiY2tueXFmMXhzMGt1MTJ1cDZ4YXkzOXJ3aiJ9.1HmCO6w6W-3r7Ou2HpRaMg'
    online_stations = Station.objects.filter(station_status="Online") 
    possiblyonline_stations = Station.objects.filter(station_status="PossiblyOnline")
    offline_stations = Station.objects.filter(station_status="Offline")
    retired_stations = Station.objects.filter(station_status="Retired")

    return render(request, 'home.html',
      { 'mapbox_access_token' : mapbox_access_token,
          'online_stations' : online_stations,
          'possiblyonline_stations' : possiblyonline_stations,
          'offline_stations' : offline_stations,
	  'retired_stations' : retired_stations,
        } )

@login_required
def profile(request):
    if request.method == 'POST':
        logger.error("POST request received")
        p_form = EditProfileForm(request.POST, instance=request.user.profile)
        if p_form.is_valid():
            logger.error(request.user.profile.email)
            request.user.profile.email = p_form.cleaned_data.get('email')
            request.user.profile.save()
            messages.success(request, 'Your Profile has been updated!')
            return redirect('profile')
        else:
            p_form = EditProfileForm(instance=request.user)
            messages.error(request, 'Issue updating information.')

        context={'p_form': p_form}
        return render(request, 'profile.html',context )
    else:
        p_form = EditProfileForm()
        return render(request, 'profile.html', {'p_form': p_form})

def activation_sent_view(request):
    return render(request, 'activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'activation_invalid.html')

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if request.POST.get("resend-button"):
            userid = request.POST.get("username")
           # userid = form.cleaned_data['username']
            try:
                user = get_object_or_404(User, username=userid)
            except:
                return render(request, 'signup.html', {'form':form})
            if user.is_active == False:

                subject = 'Please Activate Your Account'
                message = render_to_string('activation_request.html', {
                    'user': user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                # from_email = 'AB4EJ1@gmail.com'
                from_email = 'bengelke@cs.ua.edu'
                to = user.email
                msg = EmailMultiAlternatives(subject, message, from_email, [to])
                msg.send(fail_silently=False)
                return redirect('activation_sent')


        if form.is_valid() or request.POST.get("resend-button"):
            user = form.save()
            user.refresh_from_db()
            user.profile.email = form.cleaned_data.get('email')
            #set user to false until link confirmed
            user.is_active = False
            user.save()
            subject = 'Please Activate Your Account'
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            # from_email = 'AB4EJ1@gmail.com'
            from_email = "bengelke@cs.ua.edu"
            to = user.email
            msg = EmailMultiAlternatives(subject, message, from_email, [to])
            msg.send(fail_silently=False)
            return redirect('activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form':form})


def about_view(request):
    return render(request, 'about.html')

def about1_view(request):
    return render(request, 'about1.html')

@method_decorator(login_required, name='dispatch')
# Display a list of all registered users
class UserListView(SingleTableView):
    table_class = UserTable
    queryset = User.objects.all()
    template_name = 'user_list.html'
    paginate_by = 8

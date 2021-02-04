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



from .forms import SignUpForm, EditProfileForm
from .tokens import account_activation_token
from .models import Profile

import logging
logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    return render(request, 'home.html')

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
        if form.is_valid():
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
            from_email = 'colerobbinstech@gmail.com'
            to = user.email
            msg = EmailMultiAlternatives(subject, message, from_email, [to])
            msg.send(fail_silently=False)
            return redirect('activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form':form})


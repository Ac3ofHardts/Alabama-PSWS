from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('signup/', views.signup_view, name="signup"),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
]

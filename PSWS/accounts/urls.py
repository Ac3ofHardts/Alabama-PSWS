from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.contrib.auth import urls
from django.urls import path
from . import views
from .views import UserListView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
#    path('login/', auth_views.LoginView.as_view(), name='login'),
#    path('logout/', auth_views.LogoutView.as_view(template_name="registration/logout.html"), name='logout'),
#    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
#    path('password_reset_confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
#    path('password_reset_confirm/<uidb64>/set-password/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_done'),
#    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view()),
#    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('profile/', views.profile, name='profile'),
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('signup/', views.signup_view, name="signup"),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('user_list/', UserListView.as_view(), name="user_list"),
    path('about/', views.about_view, name="about"),
    path('about1/', views.about1_view, name="about1"),
    path('station_analysis/<int:id>/', views.station_analysis, name='station_analysis'),
]

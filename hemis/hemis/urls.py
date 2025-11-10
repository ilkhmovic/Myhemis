# hemis/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main.views import home,force_logout,clear_session
from accounts.views import profile_redirect

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('main.urls')),
    
    # Auth URLs
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/profile/', profile_redirect, name='profile_redirect'),
    path('force-logout/', force_logout, name='force_logout'),
    path('clear-session/', clear_session, name='clear_session'),
]
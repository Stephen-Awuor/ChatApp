from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home', views.home, name='home'),   
    path('profile/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    
   
]

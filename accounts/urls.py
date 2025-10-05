from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    

    # Root URL → redirect to login
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='root_login'),
    path("profile/", views.user_profile, name="profile"),

]

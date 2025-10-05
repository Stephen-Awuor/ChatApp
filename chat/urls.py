from django.urls import path
from chat.views import home  # 👈 import from chat
from . import views

urlpatterns = [
    path("home/", home, name="home"),
    path('logout/', views.user_logout, name='logout'),
]
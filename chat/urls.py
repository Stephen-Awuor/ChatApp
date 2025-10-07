from django.urls import path
from chat.views import home  # 👈 import from chat
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('new_group', views.create_group, name='new_group'),
    path('room/<int:room_id>/', views.room_view, name='room_view'),
    path('start_chat/<str:username>/', views.start_chat, name='start_chat'),
    path('send_message/<str:username>/', views.send_message, name='send_message'),
    path('<str:room_name>/', views.room_view, name='room'),
   
   
]
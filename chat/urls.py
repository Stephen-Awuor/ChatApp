from django.urls import path
from chat.views import home  # 👈 import from chat
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('new_group', views.create_group, name='new_group'),
    path('room/<int:room_id>/', views.start_group_chat, name='group_chat'),
    path('group_message/<int:room_id>/', views.send_group_message, name='group_message'),
    path('start_chat/<str:username>/', views.start_private_chat, name='start_chat'),
    path('send_message/<str:username>/', views.send_private_message, name='send_message'), 
]
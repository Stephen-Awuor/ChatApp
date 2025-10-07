from django.urls import path
from chat.views import home  # 👈 import from chat
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('start_chat/<str:username>/', views.start_chat, name='start_chat'),
    path('<str:room_name>/', views.room_view, name='room'),
    path('new_group', views.create_group, name='new_group'),
    path('room/<int:room_id>/', views.room_view, name='room_view'),
]
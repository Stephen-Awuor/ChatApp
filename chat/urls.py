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
    path('group_info/<int:room_id>/', views.view_group_info, name='group_info'),
    path('group/<int:room_id>/leave/', views.leave_group, name='leave-group'),
    path('add-member/<int:room_id>/', views.add_member, name='add-member'),
    path('delete-group/<int:room_id>/', views.delete_group, name='delete-group'),
    path('group/<int:room_id>/remove/<int:user_id>/', views.remove_member, name='remove-member'),
    path('invite/<int:room_id>/', views.ajax_generate_invite, name='generate_invite'),
    path('invite/ajax/<int:room_id>/', views.ajax_generate_invite, name='ajax_generate_invite'),
    path('invite/accept/<str:token>/', views.accept_invite, name='accept_invite'),
]
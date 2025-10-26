from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model() 

class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    participants = models.ManyToManyField(User, related_name='chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms', null=True, blank=True)

    def __str__(self):
        return f"{self.room_type.capitalize()} - {self.name or self.id}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
    
class ChatInvite(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='invites')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Invite for {self.room.name} by {self.invited_by.username}"

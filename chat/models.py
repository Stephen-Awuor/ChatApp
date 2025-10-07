from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model() 

class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('group', 'Group'),
        ('private', 'Private'),
    )
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='chatrooms')
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='group')

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"

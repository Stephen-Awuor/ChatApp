from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import json

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            user.is_online = True
            await sync_to_async(user.save)()
            await self.channel_layer.group_send(
                "online_status",
                {
                    "type": "user_status",
                    "user_id": user.id,
                    "is_online": True,
                },
            )
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            user.is_online = False
            await sync_to_async(user.save)()
            await self.channel_layer.group_send(
                "online_status",
                {
                    "type": "user_status",
                    "user_id": user.id,
                    "is_online": False,
                },
            )

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "user_id": event["user_id"],
            "is_online": event["is_online"],
        }))

from django.contrib.auth import get_user_model
from .models import ChatRoom

User = get_user_model()

def sidebar_context(request):
    """Makes sidebar data (rooms & users) available to all templates."""
    if not request.user.is_authenticated:
        return {}

    # Group chats where the user participates
    user_rooms = ChatRoom.objects.filter(room_type='group', participants=request.user)

    # Users available for private chats (exclude self)
    users = User.objects.exclude(id=request.user.id)

    return {
        "rooms": user_rooms,
        "users": users,
    }

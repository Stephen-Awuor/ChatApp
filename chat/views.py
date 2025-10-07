from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from .forms import GroupChatForm

User = get_user_model()

@login_required
def home(request):
    # Get all group chatrooms where the user is a participant
    user_rooms = ChatRoom.objects.filter(room_type='group', participants=request.user)
    # Get all other users for private chats
    users = User.objects.exclude(id=request.user.id)
    context = {
        "rooms": user_rooms,  # Only group chats appear in sidebar
        "users": users,       # All users for starting private chats
        "active_chat": None,
        "messages": None
    }
    return render(request, "chat/home.html", context)


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupChatForm(request.POST, user=request.user)
        if form.is_valid():
            room = form.save(commit=False)
            room.room_type = 'group'
            room.save()
            room.participants.add(request.user)  # add creator
            for participant in form.cleaned_data['participants']:
                room.participants.add(participant)
            return redirect('room_view', room_id=room.id)
    else:
        form = GroupChatForm(user=request.user)
    
    return render(request, 'chat/create_group.html', {'form': form})


@login_required
def room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.all().order_by('timestamp')
    return render(request, 'chat/group_chat.html', {'room': room, 'messages': messages})


@login_required
def start_chat(request, username):
    """Open a one-on-one private chat with a specific user"""
    other_user = get_object_or_404(User, username=username)
    current_user = request.user

    # Generate consistent private room name
    room_name = f"private_{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"

    # Either get the existing room or create a new one
    room, created = ChatRoom.objects.get_or_create(name=room_name, room_type='private')
    room.participants.add(current_user, other_user)

    # Fetch chat messages
    messages = room.messages.order_by('timestamp')

    return render(request, 'chat/private_chat.html', {
        'room': room,
        'other_user': other_user,
        'messages': messages,
    })


@login_required
def send_message(request, username):
    """Handle sending a message in a private chat"""
    if request.method == 'POST':
        other_user = get_object_or_404(User, username=username)
        current_user = request.user
        message_content = request.POST.get('message')

        room_name = f"private_{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"
        room, _ = ChatRoom.objects.get_or_create(name=room_name, room_type='private')
        room.participants.add(current_user, other_user)

        if message_content:
            Message.objects.create(room=room, sender=current_user, content=message_content)

        return redirect('start_chat', username=other_user.username)

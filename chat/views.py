from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import ChatRoom
from .forms import GroupChatForm

User = get_user_model()

@login_required
def home(request):
    # Get all chatrooms where the user is a member
    user_rooms = ChatRoom.objects.filter(members=request.user)
    # Get all other users except the current one
    users = User.objects.exclude(id=request.user.id)
    context = {
        "rooms": user_rooms,
        "users": users,
        "active_chat": None,  # default (no chat selected)
        "messages": None
    }
    return render(request, "chat/home.html", context)

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupChatForm(request.POST, user=request.user)
        if form.is_valid():
            room = form.save(commit=False)
            room.save()
            room.members.add(request.user)  # add creator
            for participant in form.cleaned_data['participants']:
                room.members.add(participant)
            return redirect('room_view', room_id=room.id)
    else:
        form = GroupChatForm(user=request.user)
    
    return render(request, 'chat/create_group.html', {'form': form})

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)

    # Generate a unique, order-independent room name
    room_name = f"private_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"

    # Create or get the chat room
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        room_type='private'
    )
    # Ensure both users are participants
    room.participants.add(request.user, other_user)
    # ✅ Redirect to the actual chat room page
    return redirect('room', room_name=room.name)

@login_required
def room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.all().order_by('timestamp') 
    return render(request, 'chat/room.html', {'room': room, 'messages': messages})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message, ChatInvite
from django.urls import reverse
from .forms import GroupChatForm
from django.contrib import messages
from .forms import AddMemberForm
from django.http import JsonResponse

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
            room.created_by = request.user  # ← Set creator as admin
            room.save()

            # Add the creator and selected participants
            room.participants.add(request.user, *form.cleaned_data['participants'])

            messages.success(request, f"Group '{room.name}' created successfully!")
            return redirect('group_info', room_id=room.id)
    else:
        form = GroupChatForm(user=request.user)

    return render(request, 'chat/create_group.html', {'form': form})

@login_required
def start_group_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.all().order_by('timestamp')
    return render(request, 'chat/group_chat.html', {'room': room, 'messages': messages})

@login_required
def send_group_message(request, room_id):
    """Handle sending a message in a group chat"""
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.method == 'POST':
        current_user = request.user
        message_content = request.POST.get('message')

        if message_content:
            Message.objects.create(room=room, sender=current_user, content=message_content)

        # After sending message, redirect back to the same chat room
        return redirect('group_chat', room_id=room.id)

    # If it's a GET request, redirect to the group chat view
    return redirect('group_chat', room_id=room.id)
 
@login_required
def start_private_chat(request, username):
    """Start or open a private chat with another user"""
    other_user = get_object_or_404(User, username=username)
    current_user = request.user

    # Always generate a deterministic room name
    room_name = f"private_{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"

    # Either get the existing room or create a new one
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'room_type': 'private', 'created_by': current_user}
    )
    room.participants.add(current_user, other_user)

    messages_qs = room.messages.order_by('timestamp')

    return render(request, 'chat/private_chat.html', {
        'room': room,
        'other_user': other_user,
        'messages': messages_qs,
    })


@login_required
def send_private_message(request, username):
    """Send a message inside a private chat"""
    other_user = get_object_or_404(User, username=username)
    current_user = request.user
    room_name = f"private_{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"

    room, _ = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'room_type': 'private', 'created_by': current_user}
    )
    room.participants.add(current_user, other_user)

    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            Message.objects.create(room=room, sender=current_user, content=content)

    return redirect('start_chat', username=other_user.username)

    
@login_required
def view_group_info(request, room_id):
    """Display group details and member list"""
    room = get_object_or_404(ChatRoom, id=room_id, room_type='group')
    members = room.participants.all()
    return render(request, 'chat/group_info.html', {'room': room, 'members': members})

@login_required
def leave_group(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='group')
    user = request.user

    if user == room.created_by:
        messages.error(request, "Group admin cannot leave the group. You can delete it instead.")
        return redirect('group_info', room_id=room.id)

    if user in room.participants.all():
        room.participants.remove(user)
        messages.success(request, f"You have left the group '{room.name}'.")
        return redirect('home')
    else:
        messages.warning(request, "You are not a member of this group.")
    return redirect('home')

@login_required
def add_member(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.method == 'POST':
        form = AddMemberForm(request.POST, room=room)
        if form.is_valid():
            participants = form.cleaned_data['participants']
            room.participants.add(*participants)
            messages.success(request, f"Added {len(participants)} new member(s) to {room.name}.")
            return redirect('group_info', room.id)
    else:
        form = AddMemberForm(room=room)

    return render(request, 'chat/add_member.html', {'form': form, 'room': room})

@login_required
def remove_member(request, room_id, user_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='group')
    if request.user != room.created_by:
        messages.error(request, "Only the group admin can remove members.")
        return redirect('group_info', room_id=room.id)

    user_to_remove = get_object_or_404(User, id=user_id)
    if user_to_remove == room.created_by:
        messages.warning(request, "Admin cannot remove themselves.")
    else:
        room.participants.remove(user_to_remove)
        messages.success(request, f"{user_to_remove.username} removed from the group.")
    return redirect('group_info', room_id=room.id)

@login_required
def delete_group(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type='group')

    if request.user != room.created_by:
        messages.error(request, "Only the group admin can delete the group.")
        return redirect('group_info', room_id=room.id)

    if request.method == 'POST':
        room.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect('home')

    return render(request, 'chat/confirm_delete_group.html', {'room': room})

@login_required
def ajax_generate_invite(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # Create a new invite
    invite = ChatInvite.objects.create(
        room=room,
        invited_by=request.user
    )

    # Build invite link
    invite_link = request.build_absolute_uri(
        reverse('accept_invite', args=[str(invite.token)])
    )

    return JsonResponse({
        'invite_link': invite_link,
        'invite_code': invite.token
    })

@login_required
def accept_invite(request, token):
    invite = get_object_or_404(ChatInvite, token=token, is_active=True)
    room = invite.room

    # Add user to the room
    room.participants.add(request.user)
    invite.is_active = False
    invite.save()

    messages.success(request, f"You’ve joined {room.name}!")
    return redirect('group_info', room_id=room.id)

@login_required
def ajax_generate_private_invite(request):
    """Generate an invite link for a private chat."""
    current_user = request.user

    # Create a temporary placeholder ChatInvite (room will be made later)
    invite = ChatInvite.objects.create(
        room=None,  # We'll assign later
        invited_by=current_user
    )

    # Build the private invite link
    invite_link = request.build_absolute_uri(
        reverse('accept_private_invite', args=[str(invite.token)])
    )

    return JsonResponse({
        'invite_link': invite_link,
        'invite_code': invite.token
    })

@login_required
def accept_private_invite(request, token):
    """Accept an invite to a private chat and create/join the room."""
    invite = get_object_or_404(ChatInvite, token=token, is_active=True)
    inviter = invite.invited_by
    invitee = request.user

    # Generate consistent room name
    room_name = f"private_{min(inviter.id, invitee.id)}_{max(inviter.id, invitee.id)}"

    # Get or create the private room
    room, _ = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={'room_type': 'private', 'created_by': inviter}
    )
    room.participants.add(inviter, invitee)

    # Mark invite as used
    invite.room = room
    invite.is_active = False
    invite.save()

    messages.success(request, f"You are now connected with {inviter.username}.")
    return redirect('start_chat', username=inviter.username)





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message, ChatInvite
from django.urls import reverse
from .forms import GroupChatForm
from django.contrib import messages
from .forms import AddMemberForm
from django.http import JsonResponse
import uuid
from openai import OpenAI
from dotenv import load_dotenv
import os
from django.views.decorators.http import require_GET


load_dotenv()  # Load .env values
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
User = get_user_model()

@login_required
def home(request):
    return render(request, "chat/home.html")

@login_required
@require_GET
def search_groups(request):
    query = request.GET.get("q", "").strip()
    rooms = ChatRoom.objects.filter(room_type='group', participants=request.user)

    if query:
        rooms = rooms.filter(name__icontains=query)

    data = [
        {"id": r.id, "name": r.name, "members": r.participants.count()}
        for r in rooms
    ]
    return JsonResponse({"groups": data})

@login_required
@require_GET
def search_chats(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.exclude(id=request.user.id)

    if query:
        users = users.filter(username__icontains=query)

    data = [
        {"username": u.username}
        for u in users
    ]
    return JsonResponse({"chats": data})

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
    invite = ChatInvite.objects.create(room=room, invited_by=request.user)

    invite_link = request.build_absolute_uri(
        reverse('accept_invite', args=[str(invite.token)])
    )

    return JsonResponse({
        'invite_link': invite_link,
        'invite_code': invite.token
    })

@login_required
def accept_invite(request, token):
    # Get invite (whether or not user came from redirect)
    invite = get_object_or_404(ChatInvite, token=token, is_active=True)
    room = invite.room

    # ✅ Add the user to participants if not already
    if request.user not in room.participants.all():
        room.participants.add(request.user)
        messages.success(request, f"You’ve joined {room.name}!")
    else:
        messages.info(request, f"You are already a member of {room.name}.")

    # ✅ Deactivate the invite AFTER successful join
    invite.is_active = False
    invite.save()

    # Redirect straight to group chat page
    return redirect('group_chat', room_id=room.id)

@login_required
def ajax_generate_private_invite(request):
    """Generate an invite link for a private chat."""
    try:
        # Create a new invite (no room yet, private chat type)
        invite = ChatInvite.objects.create(
            invited_by=request.user,
            token=str(uuid.uuid4()),
        )

        # Build full invite link
        invite_link = request.build_absolute_uri(
            reverse('accept_private_invite', args=[invite.token])
        )

        return JsonResponse({
            'invite_link': invite_link,
            'invite_code': invite.token,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def accept_private_invite(request, token):
    """Accept a private chat invite and start or open a 1-on-1 chat."""
    invite = get_object_or_404(ChatInvite, token=token, is_active=True)
    inviter = invite.invited_by
    invited_user = request.user

    if inviter == invited_user:
        return redirect('home')

    # Check if a private room between the two already exists
    existing_room = (
        ChatRoom.objects.filter(room_type='private')
        .filter(participants=inviter)
        .filter(participants=invited_user)
        .distinct()
        .first()
    )

    if existing_room:
        room = existing_room
    else:
        # Create a new private room
        room_name = f"Private Chat: {inviter.username} & {invited_user.username}"
        room = ChatRoom.objects.create(
            name=room_name,
            room_type='private',
            created_by=inviter
        )
        room.participants.add(inviter, invited_user)

    # Mark invite as used (optional)
    invite.is_active = False
    invite.room = room
    invite.save()

    # Redirect to the private chat room
    return redirect('start_chat', username=inviter.username)

def ai_chat(request):
    """Render the Smart Assistant chat UI"""
    return render(request, "chat/ai_chat.html")


@login_required
def ai_response(request):
    """Handle user messages and return AI responses"""
    if request.method == "POST":
        user_message = request.POST.get("message", "")
        if not user_message:
            return JsonResponse({"error": "No message provided."}, status=400)

        try:
            # Use the new API client (correct syntax)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # You can also use "gpt-4-turbo" or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant integrated into a chat app."},
                    {"role": "user", "content": user_message},
                ]
            )

            ai_message = response.choices[0].message.content
            return JsonResponse({"reply": ai_message})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request."}, status=400)



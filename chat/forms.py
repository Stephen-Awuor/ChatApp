from django import forms
from django.contrib.auth import get_user_model
from .models import ChatRoom

User = get_user_model()

class GroupChatForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ChatRoom
        fields = ['name', 'participants']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Don’t show current user in list
        if user:
            self.fields['participants'].queryset = User.objects.exclude(id=user.id)

class AddMemberForm(forms.Form):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # will set dynamically in __init__
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Members"
    )

    def __init__(self, *args, **kwargs):
        room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
        if room:
            # Exclude users who are already participants
            existing_members = room.participants.all()
            self.fields['participants'].queryset = User.objects.exclude(id__in=existing_members)
        else:
            # fallback, show all users if no room is passed
            self.fields['participants'].queryset = User.objects.all()

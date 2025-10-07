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

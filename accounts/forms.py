from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.hashers import make_password

User = get_user_model()

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Display Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email address",
            "required": "true"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "required": "true"
        })
    )

class ProfileForm(forms.ModelForm):
    old_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Current Password"})
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New Password"})
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm New Password"})
    )
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "avatar"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter display name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email"
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        # If user entered a new password, validate it
        if new_password1 or new_password2:
            if not old_password:
                raise forms.ValidationError("Please enter your current password to change it.")
            if not self.user.check_password(old_password):
                raise forms.ValidationError("Your current password is incorrect.")
            if new_password1 != new_password2:
                raise forms.ValidationError("The new passwords do not match.")
            password_validation.validate_password(new_password1, self.user)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password1 = self.cleaned_data.get("new_password1")

        # Change password if user provided one
        if new_password1:
            user.set_password(new_password1)
        if commit:
            user.save()
        return user
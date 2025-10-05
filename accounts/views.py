from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import SignupForm, EmailLoginForm, ProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request, data=request.POST)  # 👈 use EmailLoginForm
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
    else:
        form = EmailLoginForm()
    return render(request, "accounts/login.html", {"form": form})

@login_required
def user_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep logged in
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(request.user, instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})




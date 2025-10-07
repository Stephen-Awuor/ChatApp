from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from .forms import SignupForm, EmailLoginForm, ProfileForm
from django.contrib import messages

User = get_user_model()

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return redirect("login")
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
def home(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/home.html', {'users': users})

def user_logout(request):
    logout(request)
    return redirect('login')  

@login_required
def user_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, user=request.user, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("profile")
        else:
            # Display detailed validation errors
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = ProfileForm(user=request.user, instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})
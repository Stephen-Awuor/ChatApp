from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "chat/home.html")  # or accounts/home.html if you moved it

def user_logout(request):
    logout(request)
    return redirect('login')  
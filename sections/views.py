from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Section
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages\

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, "registration/login.html", {"form": form})



def educationalsection(request):

    sections = Section.objects.all().order_by('category', 'id')
    
    
    grouped_sections = defaultdict(list)
    for section in sections:
        grouped_sections[section.category].append(section)
    
    
    grouped_sections = dict(grouped_sections)
    
    return render(request, "users/educationalsection.html", {
        "grouped_sections": grouped_sections
    })

def home_view(request):
    return render(request, 'users/home.html')

def search_view(request):
    return render(request, 'users/search.html')

def activities_view(request):
    return render(request, 'users/activities.html')

@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "users/profile.html", {"user": user})


def about_view(request):
    return render(request, 'users/about.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

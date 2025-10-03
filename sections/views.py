from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Section
from collections import defaultdict

def section_list(request):
    # Fetch all sections and order by category and id
    sections = Section.objects.all().order_by('category', 'id')
    
    # Group sections by category
    grouped_sections = defaultdict(list)
    for section in sections:
        grouped_sections[section.category].append(section)
    
    # Convert to regular dict for template
    grouped_sections = dict(grouped_sections)
    
    return render(request, "sections/section_list.html", {
        "grouped_sections": grouped_sections
    })

def home_view(request):
    return render(request, 'home.html')

def search_view(request):
    return render(request, 'search.html')

def activities_view(request):
    return render(request, 'activities.html')

def profile_view(request):
    return render(request, 'profile.html')

def about_view(request):
    return render(request, 'about.html')

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

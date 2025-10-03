from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.section_list, name='section_list'),  # default page for /sections/
    path('home/', lambda request: render(request, 'sections/home.html'), name='home'),
    path('search/', lambda request: render(request, 'sections/search.html'), name='search'),
    path('activities/', lambda request: render(request, 'sections/activities.html'), name='activities'),
    path('profile/', lambda request: render(request, 'sections/profile.html'), name='profile'),
    path('about/', lambda request: render(request, 'sections/about.html'), name='about'),
]

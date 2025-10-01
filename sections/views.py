from django.shortcuts import render
from .models import Section

def section_list(request):
    sections = Section.objects.all()
    return render(request, "sections/section_list.html", {"sections": sections})

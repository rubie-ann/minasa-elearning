from django.contrib import admin
from .models import Section

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    search_fields = ("title", "description")
    list_filter = ("category",)

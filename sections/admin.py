from django.contrib import admin
from .models import Section, Profile
from django.utils.html import format_html
from .models import FestivalEvent, Category, Quiz, Question, Answer
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "attachment_link", "link_display")
    search_fields = ("title", "description")
    list_filter = ("category",)

    def attachment_link(self, obj):
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.attachment.url)
        return "-"
    attachment_link.short_description = "Attachment"

    def link_display(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.link, obj.link)
        return "-"
    link_display.short_description = "Link"

@admin.register(FestivalEvent)
class FestivalEventAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "date", "time", "location")
    search_fields = ("name", "description", "location")
    list_filter = ("event_type", "date")
    date_hierarchy = "date"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    fields = ("name", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_superuser", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    
    # Add helpful message for admin user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_by", "created_at")
    search_fields = ("title", "description")
    list_filter = ("created_by", "created_at")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "text", "order")
    search_fields = ("text",)
    list_filter = ("quiz",)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")
    search_fields = ("text",)
    list_filter = ("question__quiz", "is_correct")

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

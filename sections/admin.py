from django.contrib import admin
from .models import Section, Profile, MinasaProduct
from django.utils.html import format_html
from .models import FestivalEvent, Category, Quiz, Question, Answer, MinigameLevel
from .models import Feedback
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import GrowthStage
from django import forms

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

# Register MinasaProduct model - THIS IS THE IMPORTANT ONE
@admin.register(MinasaProduct)
class MinasaProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'image', 'id')
    search_fields = ('product_name', 'description')
    list_filter = ('price',)
    ordering = ('-id',)
    
    # Optional: Make the admin interface more user-friendly
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'description', 'price')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )

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

class MinigameLevelForm(forms.ModelForm):
    class Meta:
        model = MinigameLevel
        fields = ['image1', 'image2', 'image3', 'image4', 'answer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields.values():
            field.required = True

@admin.register(MinigameLevel)
class MinigameLevelAdmin(admin.ModelAdmin):
    form = MinigameLevelForm
    list_display = ("id", "answer", "image1_preview", "image2_preview", "image3_preview", "image4_preview", "created_at")
    search_fields = ("answer",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    def image1_preview(self, obj):
        if obj.image1:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image1.url)
        return "-"
    image1_preview.short_description = "Image 1"

    def image2_preview(self, obj):
        if obj.image2:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image2.url)
        return "-"
    image2_preview.short_description = "Image 2"

    def image3_preview(self, obj):
        if obj.image3:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image3.url)
        return "-"
    image3_preview.short_description = "Image 3"

    def image4_preview(self, obj):
        if obj.image4:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image4.url)
        return "-"
    image4_preview.short_description = "Image 4"

@admin.register(GrowthStage)
class GrowthStageAdmin(admin.ModelAdmin):
    list_display = ('date', 'title')
    ordering = ('date',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_sender', 'email', 'created_at', 'resolved')
    list_filter = ('resolved', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'user', 'created_at')
    actions = ('mark_resolved',)

    def short_sender(self, obj):
        return obj.user.username if obj.user else (obj.name or 'Anonymous')
    short_sender.short_description = 'Sender'

    def mark_resolved(self, request, queryset):
        updated = queryset.update(resolved=True)
        self.message_user(request, f'{updated} feedback item(s) marked resolved.')
    mark_resolved.short_description = 'Mark selected feedback as resolved'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)



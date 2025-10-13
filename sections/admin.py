from django.contrib import admin
from .models import Section
from django.utils.html import format_html

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

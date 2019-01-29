from django.contrib import admin

from ccc.ocr.models import ImageContacts

# Register your models here.


class ImageContactsAdmin(admin.ModelAdmin):
    list_display = ["created_at", 'campaign__name', 'survey__name', "image", "unique_upload_id", ]
    search_fields = ["unique_upload_id"]

    def campaign__name(self, obj):
        if obj.campaign:
            return obj.campaign.name
        return ''

    def survey__name(self, obj):
        if obj.survey:
            return obj.survey.title
        return ''


admin.site.register(ImageContacts, ImageContactsAdmin)

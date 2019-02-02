from django.contrib import admin

from .models import PlannedPost


@admin.register(PlannedPost)
class PlannedPostAdmin(admin.ModelAdmin):
    list_filter = 'bot',
    list_display = '__str__', 'bot',

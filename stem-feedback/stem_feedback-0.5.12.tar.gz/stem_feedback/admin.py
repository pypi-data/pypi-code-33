from django.contrib import admin
from .models import *


@admin.register(FeedBackType)
class FeedBackTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email',)
    fields = ['feedback_type', 'name', 'email', 'desc']

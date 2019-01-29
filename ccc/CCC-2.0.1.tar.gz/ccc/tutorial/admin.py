from adminsortable.admin import SortableAdmin
from django.contrib import admin

from ccc.tutorial.models import Video


class VideoAdmin(SortableAdmin):
    list_display = ['title', 'video', 'user', 'in_popup']


admin.site.register(Video, VideoAdmin)

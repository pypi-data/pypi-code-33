from django.contrib import admin

from . import models


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'category', 'create_time')
    raw_id_fields = ('party','category')
    search_fields = ("name",)
    readonly_fields = ('party',)


admin.site.register(models.Course, CourseAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)
    readonly_fields = ('party',)


admin.site.register(models.Category, CategoryAdmin)


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name','create_time')
    raw_id_fields = ('party', 'course')


admin.site.register(models.Chapter, ChapterAdmin)

 
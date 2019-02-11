from django.contrib import admin
from .models import *


class FeatureInline(admin.TabularInline):
    model = Feature


class ProjectAdmin(admin.ModelAdmin):
    inlines = [FeatureInline,]
    prepopulated_fields = {"slug": ("title",)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Feature)


admin.site.register(Project, ProjectAdmin)

admin.site.register(Customer)

admin.site.register(Category, CategoryAdmin)

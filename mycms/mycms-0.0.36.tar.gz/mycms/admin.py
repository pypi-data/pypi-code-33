from django.contrib import admin
from .models import CMSPageTypes
from .models import CMSContents
from .models import CMSEntries
from .models import CMSMarkUps
from .models import CMSTemplates
from .models import CMSPaths

@admin.register(CMSPaths)
class CMSPathsAdmin(admin.ModelAdmin):
    list_display = ["id", "path", "parent"]

@admin.register(CMSContents)
class CMSContents(admin.ModelAdmin):
    list_display = ["id", "title","timestamp", "markup", "page"]
    list_filter=["title","markup"]
    
    
def make_published(modeladmin, request, queryset):
    queryset.update(published=True)
    
make_published.short_description= "Publish Selected CMSEntries"
    
@admin.register(CMSEntries)
class CMSEntries(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'path', 'page_type', 'published', 'frontpage']
    list_filter =["page_type", "template"]

    actions = [make_published]

@admin.register(CMSMarkUps)
class CMSMarkUps(admin.ModelAdmin):
    pass

@admin.register(CMSTemplates)
class CMSTemplates(admin.ModelAdmin):
    pass

@admin.register(CMSPageTypes)
class CMSPageTypesAdmin(admin.ModelAdmin):
    list_filter = ("page_type", "text", "view_class")
    list_display = ['id','page_type', 'text', 'view_class', 'view_template']
    


    

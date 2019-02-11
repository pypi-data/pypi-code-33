from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import Publishable, Post, Category, Article, Note


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    fields = ['parent', 'title', 'slug', 'excerpt', 'image']


def publish_selected(modeladmin, request, queryset):
    for object in queryset:
        object.set_status(Publishable.STATUS_PUBLISHED)


publish_selected.short_description = 'Publier'


def draft_selected(modeladmin, request, queryset):
    for object in queryset:
        object.set_status(Publishable.STATUS_DRAFT)


draft_selected.short_description = 'Passer en Brouillon'


class PublishableAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'status', 'published_at', 'modified_at', 'modified_by', 'created_at', 'created_by')
    list_filter = ('categories', 'status')
    ordering = ('-created_at',)
    exclude = ('created_by', 'created_at', 'modified_at', 'modified_by')
    actions = (publish_selected, draft_selected)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            if form.changed_data:
                obj.modified_by = request.user

        super().save_model(request, obj, form, change)


class ArticleAdmin(MPTTModelAdmin, PublishableAdmin):
    fieldsets = (
        ('', {
            'fields': ('parent', 'title', 'excerpt', 'content')
        }),
        ('Publication', {
            'fields': ('image', 'categories', 'can_comment', 'slug', 'status')
        }),
    )


class PostAdmin(PublishableAdmin):
    fieldsets = (
        ('', {
            'fields': ('title', 'excerpt', 'content')
        }),
        ('Publication', {
            'fields': ('image', 'categories', 'can_comment', 'slug', 'status')
        }),
    )


admin.site.register(Category, CategoryAdmin)

admin.site.register(Article, ArticleAdmin)

admin.site.register(Post, PostAdmin)

admin.site.register(Note)

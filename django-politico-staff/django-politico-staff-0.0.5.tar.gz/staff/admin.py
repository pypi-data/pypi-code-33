from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from staff.models import Profile

from .celery import sync_slack_users


class ProfileInlineAdmin(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "user profile"
    fieldsets = (
        (None, {"fields": ("user",)}),
        ("Politico", {"fields": ("politico_title", "politico_author_page")}),
        ("Slack", {"fields": ("slack_api_id", "slack_image")}),
        ("Google", {"fields": ("google_email", "google_display_name")}),
        ("Twitter", {"fields": ("twitter_handle",)}),
    )
    readonly_fields = ("slack_api_id", "slack_image")


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInlineAdmin,)

    actions = ["sync_slack_profile"]

    def sync_slack_profile(self, request, queryset):
        sync_slack_users.delay([user.pk for user in queryset])
        self.message_user(request, "Synced with Slack")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

import json

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .controllers import rerun_logged_task
from .models import LoggedTask


class LoggedTaskAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "queue",
        "task_name",
        "created_at",
        "args",
        "kwargs",
        "status",
    )
    list_filter = ("task_name", "status")

    fields = readonly_fields = (
        "id",
        "queue",
        "created_at",
        "task_name",
        "admin_args",
        "admin_kwargs",
        "admin_stacktrace",
        "status",
        "admin_rollbar",
    )
    ordering = ("-created_at",)

    actions = ["delete_selected", "retry_logged_tasks"]

    def retry_logged_tasks(logged_task_admin, request, queryset):
        opts = logged_task_admin.model._meta

        if request.method == "POST":
            for logged_task in queryset:
                rerun_logged_task(logged_task)
            count = queryset.count()
            message = "Retried {} Logged Task items".format(count)
            logged_task_admin.message_user(request, message, messages.SUCCESS)
            # Return None to display the change list page again.
            return None

        context = {
            "title": "Retry Tasks?",
            "queryset": queryset,
            "opts": opts,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": logged_task_admin.media,
        }

        return TemplateResponse(
            request,
            "admin/retry_task_confirmation.html",
            context=context,
            current_app=logged_task_admin.admin_site.name,
        )

    def admin_stacktrace(self, logged_task):
        return format_html("<br/><pre>{}</pre>", logged_task.stacktrace)

    def admin_args(self, logged_task):
        args = json.loads(logged_task.args)
        return format_html("<br/><pre>{}</pre>", json.dumps(args, indent=4))

    def admin_kwargs(self, logged_task):
        kwargs = json.loads(logged_task.kwargs)
        return format_html("<br/><pre>{}</pre>", json.dumps(kwargs, indent=4))

    def admin_rollbar(self, logged_task):
        if not logged_task.rollbar_occurrence:
            return "No Rollbar occurrence logged"
        return format_html(
            "<a href='https://rollbar.com/occurrence/uuid/?uuid={}'>Rollbar occurrence</a>",
            logged_task.rollbar_occurrence,
        )

    retry_logged_tasks.short_description = "Retry Selected Tasks"


admin.site.register(LoggedTask, LoggedTaskAdmin)

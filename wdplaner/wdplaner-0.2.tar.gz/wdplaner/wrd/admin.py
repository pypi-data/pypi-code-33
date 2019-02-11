from datetime import timedelta
from django.conf import settings

from django.contrib import admin, messages

# Register your models here.
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from sesame import utils as sesame_utils


from wrd.models import Episode, Application, ApplicationAttachment, DropboxFile


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("name", "table_link", "begin", "end", "days")

    def table_link(self, object):
        return mark_safe(
            '<a href="'
            + reverse("admin:wrd_episode_table", args=(object.pk,))
            + '">Tabelle</a>'
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("<int:pk>/table/", self.table, name="wrd_episode_table")]
        return my_urls + urls

    def table(self, request, pk):
        episode = self.model.objects.get(pk=pk)
        context = dict(
            self.admin_site.each_context(request),
            episode=episode,
            days=episode.day_list(),
            dayct=episode.day_list_ct(),
            title=episode.__str__(),
        )
        return TemplateResponse(request, "admin/application_table.html", context)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "episode",
        "user",
        "application_status",
        "eh_ok",
        "drsa_ok",
        "arrival",
        "departure",
        "days",
    )

    change_form_template = "admin/application_changeform.html"

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(
                reverse("admin:wrd_episode_table", args=[obj.episode.pk])
            )
        else:
            return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if "_generateuserurl" in request.POST:
            token_suffix = sesame_utils.get_query_string(obj.user)
            path = obj.get_absolute_url() + token_suffix
            days_valid = settings.SESAME_MAX_AGE / (24 * 3600)
            url = request.build_absolute_uri(path)
            messages.success(
                request,
                mark_safe(
                    f'Login-URL (gültig für {days_valid} Tage): <a href="{url}">{url}</a>'
                ),
            )
        elif (
            "_continue" not in request.POST
            and "_saveasnew" not in request.POST
            and "_addanother" not in request.POST
        ):
            return HttpResponseRedirect(
                reverse("admin:wrd_episode_table", args=[obj.episode.pk])
            )
        return super().response_change(request, obj)


@admin.register(DropboxFile)
class DropboxFileAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "path_display",
        "server_modified",
        "file_id",
        "content_hash",
    ]


@admin.register(ApplicationAttachment)
class ApplicationAttachmentAdmin(admin.ModelAdmin):
    list_display = ["application", "dropbox_file", "attachment_type"]

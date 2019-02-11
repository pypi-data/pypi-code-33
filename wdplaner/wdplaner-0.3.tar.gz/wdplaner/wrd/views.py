import dropbox
import mimetypes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, HTML
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import UpdateView
from urllib.parse import quote

from wrd.models import Application, Episode, ApplicationAttachment


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            context["episodes"] = Episode.objects.all()

        return context


class EpisodeDetail(LoginRequiredMixin, DetailView):
    model = Episode

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Http404()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["days"] = self.object.day_list()
        context["dayct"] = self.object.day_list_ct()
        return context


class ApplicationDetail(LoginRequiredMixin, DetailView):
    model = Application

    def get_queryset(self):
        if not self.request.user.is_staff:
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()


class EditApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    "Allgemein",
                    "arrival",
                    "departure",
                    "role",
                    "comment",
                    css_class="col-lg-6",
                ),
                Fieldset(
                    "Status",
                    "application_status",
                    "drsa_ok",
                    "eh_ok",
                    css_class="col-lg-6",
                ),
            ),
            ButtonHolder(
                Submit("submit", "Speichern"),
                HTML(
                    '<a class="btn btn-outline-secondary" href="{% url \'application-detail\' object.pk %}">Abbrechen</a>'
                ),
            ),
        )

    class Meta:
        model = Application
        fields = [
            "arrival",
            "departure",
            "application_status",
            "role",
            "comment",
            "eh_ok",
            "drsa_ok",
        ]


class ApplicationEditView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = EditApplicationForm

    def form_valid(self, form):
        messages.success(self.request, "Änderungen gespeichert")
        return super().form_valid(form)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Http404()
        return super().get_queryset()


class ApplicationList(LoginRequiredMixin, ListView):
    model = Application

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class DownloadAttachmentView(LoginRequiredMixin, DetailView):
    model = ApplicationAttachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        mimetypes.init()
        t, _ = mimetypes.guess_type(self.object.dropbox_file.name)

        dbx = dropbox.Dropbox(settings.DROPBOX_AUTH_TOKEN)

        safe_filename = quote(self.object.dropbox_file.name)
        meta, res = dbx.files_download(self.object.dropbox_file.path_display)
        with res:
            res = HttpResponse(res, content_type=t)
            res[
                "Content-Disposition"
            ] = f'inline; filename="{safe_filename}"'
            return res

    def get_queryset(self):
        if not self.request.user.is_staff:
            return super().get_queryset().filter(application__user=self.request.user)
        return super().get_queryset()

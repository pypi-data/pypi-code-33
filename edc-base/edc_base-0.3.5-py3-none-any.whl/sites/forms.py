from django import forms
from django.contrib.sites.models import Site

from .raise_on_save_if_reviewer import raise_on_save_if_reviewer
from .raise_on_save_if_reviewer import ReviewerSiteSaveError


class SiteModelFormMixin:
    def clean(self):
        site = Site.objects.get_current()
        try:
            raise_on_save_if_reviewer(site_id=site.id)
        except ReviewerSiteSaveError:
            raise forms.ValidationError(
                "Adding or changing data has been disabled. "
                f"See Site configuration. Got '{site.name.title()}'."
            )
        return super().clean()

import re

from django.db import models
from django.utils.translation import ugettext_lazy
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core import models as wagtailmodels
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmetadata.models import MetadataPageMixin


class Page(MetadataPageMixin, wagtailmodels.Page):
    """
    A base page with social metadata and a more sensible default template.
    """

    # Disable the creation of the related field accessor on Page
    # This prevents conflicts with model names and field names
    page_ptr = models.OneToOneField(wagtailmodels.Page, parent_link=True,
                                    related_name='+', on_delete=models.CASCADE)

    # We override promote panels to remove show_in_menus
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            ImageChooserPanel('search_image'),  # From MetadataPageMixin
        ], ugettext_lazy('Common page configuration')),
    ]

    def get_template(self, request, *args, **kwargs):
        """
        Templates are named like ``layouts/app/model.html``.
        """
        label = self._meta.label.split('.')
        app = label[0]
        model_name = '_'.join(re.findall('^[a-z]+|[A-Z][^A-Z]*', label[1])).lower()
        return "layouts/{}/{}.html".format(app, model_name)

    class Meta:
        abstract = True

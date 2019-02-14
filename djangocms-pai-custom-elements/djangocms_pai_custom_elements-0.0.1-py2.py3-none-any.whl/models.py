# -*- coding: utf-8 -*-
"""
Enables the user to add style plugin that displays a html tag with
the provided settings from the style plugin.
"""
from __future__ import unicode_literals

import os
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from djangocms_attributes_field.fields import AttributesField

from cms.models import CMSPlugin


class Attribute(AttributesField):
    def validate_key(self, key):
        pass

@python_2_unicode_compatible
class CustomElement(CMSPlugin):
    """
    Renders a given ``TAG_CHOICES`` element with additional attributes
    """
    class Meta:
        abstract = True
        
    tag_type = 'custom-element'
    template = 'custom-element.html'

    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        max_length=255,
        help_text=_('Overrides the display name in the structure mode.'),
    )
    classes = models.CharField(
        verbose_name=_('Additional classes'),
        blank=True,
        max_length=255,
        help_text=_('Additional comma separated list of classes '
            'to be added to the element e.g. "row, column-12, clearfix".'),
    )
    id_name = models.CharField(
        verbose_name=_('ID name'),
        blank=True,
        max_length=255,
    )
    attributes = Attribute(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['class', 'id', 'style'],
    )
    js = models.TextField(null=True, blank=True)
    css = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.label


class GenericCustomElement(CustomElement):

    tag_type = models.CharField(verbose_name=_('Tag type'), max_length=255)
    template = models.CharField(verbose_name=_('Template'), max_length=255, default='generic-custom-element.html')

    js_asset = models.FileField(verbose_name=_('JS asset'), null=True, blank=True, upload_to=os.path.join('custom_elements', 'js_assets'))
    css_asset = models.FileField(verbose_name=_('CSS asset'), null=True, blank=True, upload_to=os.path.join('custom_elements', 'css_assets'))
    
    async_load = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Generic CustomElement')
        verbose_name_plural = _('Generic CustomElements')

"""
class ExampleCustomElement(CustomElement):

    class Meta:
        verbose_name = _('Example CustomElement')
        verbose_name_plural = _('Example CustomElements')

    tag_type = 'example-element'
    template = 'example-element.html'
"""

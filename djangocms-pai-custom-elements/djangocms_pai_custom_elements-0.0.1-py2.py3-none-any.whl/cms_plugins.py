# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from .models import GenericCustomElement


class CustomElementPlugin(CMSPluginBase):
    name = _('Custom Element')
    
    fieldsets = (
        (None, {
            'fields': (
                'label', 'id_name',
                ('classes', 'attributes'),
                ('js', 'css'),
            ),
        }),
    )

    def get_render_template(self, context, instance, placeholder):
        return 'custom_elements/elements/{}'.format(instance.template)



class GenericCustomElementPlugin(CustomElementPlugin):
    model = GenericCustomElement
    name = _('Generic custom element')
        
    fieldsets = (
        (None, {
            'fields': (
                'tag_type',
                'label', 'id_name',
                ('classes', 'attributes'),
                ('js_asset', 'css_asset'),
                ('js', 'css'),
                'async_load',
            ),
        }),
    )
    
    allow_children = True

plugin_pool.register_plugin(GenericCustomElementPlugin)


# -*- coding: utf-8 -*-
from lxml import etree
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import lxml
import requests


class EmbeddedPageView(BrowserView):

    template = ViewPageTemplateFile('embeddedpage.pt')

    def __call__(self):
        response = requests.get(self.context.url)
        # Normalize charset to unicode
        content = safe_unicode(response.content)
        # Turn to utf-8
        content = content.encode('utf-8')
        el = lxml.html.fromstring(content)
        if el.find('body'):
            el = el.find('body')
        self.embeddedpage = etree.tostring(el)
        return self.template()

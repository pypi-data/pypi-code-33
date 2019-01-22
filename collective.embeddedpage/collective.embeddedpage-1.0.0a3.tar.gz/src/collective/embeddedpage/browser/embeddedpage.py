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
        # we receive a utf-8 encoded string from requests
        # lxml expect unicode though
        content = safe_unicode(response.content)
        subtree = lxml.html.fromstring(content).find('body')
        self.embeddedpage = etree.tostring(subtree)
        return self.template()

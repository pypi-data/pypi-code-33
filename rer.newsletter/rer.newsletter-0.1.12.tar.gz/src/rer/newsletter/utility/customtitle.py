# -*- coding: utf-8 -*-
from plone import api
from zope.interface import implementer
from zope.interface import Interface

import json


class ICustomTitle(Interface):

    def titleLang(json_string):
        """
        from json field return string

        Args:
          json_string (str): json field title

        Returns:
          string: that rapresent value
        """


@implementer(ICustomTitle)
class CustomTitleHandler(object):
    def _current_lang(self):
        return api.portal.get_current_language()

    def titleLang(self, json_string):
        """ return site title """
        try:
            site_title = json.loads(json_string)

            if self._current_lang() not in site_title.keys() and 'default' in site_title.keys():  # noqa
                site_title = site_title.get('default', None)
            elif self._current_lang() in site_title.keys():
                site_title = site_title.get(
                    self._current_lang(), None)
            else:
                site_title = 'Plone Site'
        except ValueError:
            site_title = json_string

        return site_title

""" geotags JSON related views
"""

import json
from Products.Five.browser import BrowserView
from eea.geotags.vocabularies.interfaces import IGeoCountriesMapping


class CountryMappings(BrowserView):
    """ Geotags country mappings view
    """

    def __call__(self, *args, **kwargs):
        """
        :return: json dict of country mappings
        :rtype: dict
        """
        vocab = IGeoCountriesMapping(self.context)()
        res = {term.value: term.title for term in vocab}
        return json.dumps(res)

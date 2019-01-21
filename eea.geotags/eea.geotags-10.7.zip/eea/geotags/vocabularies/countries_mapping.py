""" Countries
"""
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from plone.registry.interfaces import IRegistry
from eea.geotags.vocabularies.interfaces import IGeoCountriesMapping
from eea.geotags.controlpanel.interfaces import IGeoVocabularies


class Countries_Mapping(object):
    """ Extract countries for group
    """
    implements(IGeoCountriesMapping)

    def __init__(self, context):
        self.context = context

    def __call__(self):

        registry = getUtility(IRegistry).forInterface(IGeoVocabularies, False)
        countries_mapping = registry.countries_mapping or dict()
        items = [
            SimpleTerm(key, key, val)
            for key, val in countries_mapping.items()
        ]
        return SimpleVocabulary(items)

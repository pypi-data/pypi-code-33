""" Countries
"""
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from plone.registry.interfaces import IRegistry
from eea.geotags.vocabularies.interfaces import IGeoCountries
from eea.geotags.controlpanel.interfaces import IGeoVocabularies


class Countries(object):
    """ Extract countries for group
    """
    implements(IGeoCountries)

    def __init__(self, context):
        self.context = context

    def __call__(self, group=''):
        registry = getUtility(IRegistry).forInterface(IGeoVocabularies, False)
        geotags = registry.geotags or dict()
        items = [
            SimpleTerm(key, key, val)
            for key, val in geotags.get(group, dict()).items()
            if key != 'title' # exclude the group title
        ]
        return SimpleVocabulary(items)

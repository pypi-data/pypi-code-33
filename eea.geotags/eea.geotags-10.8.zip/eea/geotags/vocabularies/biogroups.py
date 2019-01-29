""" Groups
"""
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from plone.registry.interfaces import IRegistry

from eea.geotags.vocabularies.interfaces import IBioGroups
from eea.geotags.controlpanel.interfaces import IGeoVocabularies


class BioGroups(object):
    """ Biogeographical regions
    """
    implements(IBioGroups)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        registry = getUtility(IRegistry).forInterface(IGeoVocabularies, False)
        biotags = registry.biotags or dict()
        items = [
            SimpleTerm(key, key, val['title'])
            for key, val in biotags.items()
        ]
        return SimpleVocabulary(items)

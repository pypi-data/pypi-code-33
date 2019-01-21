""" Groups
"""
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from plone.registry.interfaces import IRegistry
from eea.geotags.vocabularies.interfaces import IGeoGroups
from eea.geotags.controlpanel.interfaces import IGeoVocabularies


class Groups(object):
    """ Extract countries for group
    """
    implements(IGeoGroups)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        registry = getUtility(IRegistry).forInterface(IGeoVocabularies, False)
        geotags = registry.geotags or dict()
        items = [
            SimpleTerm(key, key, val['title'])
            for key, val in geotags.items()
        ]
        return SimpleVocabulary(items)

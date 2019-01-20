from plone.indexer.decorator import indexer
from collective import dexteritytextindexer
from zope.component import adapts
from zope.interface import implements

from .behaviors import IOrganisation


@indexer(IOrganisation)
def founders(obj):
    return obj.founders


@indexer(IOrganisation)
def organisation_type(obj):
    return obj.organisation_type


@indexer(IOrganisation)
def industry(obj):
    return obj.industry

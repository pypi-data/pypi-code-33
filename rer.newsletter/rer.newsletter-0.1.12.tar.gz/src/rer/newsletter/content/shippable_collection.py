# -*- coding: utf-8 -*-
from plone.app.contenttypes.content import Collection
from rer.newsletter.interfaces import IShippableCollection
from zope.interface import implementer


@implementer(IShippableCollection)
class ShippableCollection(Collection):
    pass

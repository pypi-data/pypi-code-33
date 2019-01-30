# -*- coding: utf-8 -*-
from .interfaces import INotifyOnSubscribe
from .interfaces import INotifyOnUnsubscribe
from OFS.SimpleItem import SimpleItem
from plone.contentrules.rule.interfaces import IRuleElementData
from zope.interface import implementer


@implementer(INotifyOnSubscribe, IRuleElementData)
class NotifyOnSubscribeAction(SimpleItem):

    subject = u''
    source = u''
    dest_addr = u''
    message = u''

    element = 'plone.actions.NotificationOnSubscribe'

    @property
    def summary(self):
        return u'Send email for user subscribe'


@implementer(INotifyOnUnsubscribe, IRuleElementData)
class NotifyOnUnsubscribeAction(SimpleItem):

    subject = u''
    source = u''
    dest_addr = u''
    message = u''

    element = 'plone.actions.NotificationOnUnsubscribe'

    @property
    def summary(self):
        return u'Send email for user unsubscribe'

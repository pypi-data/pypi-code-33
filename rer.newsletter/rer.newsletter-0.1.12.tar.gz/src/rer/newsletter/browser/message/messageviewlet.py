# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from plone import api
from plone.app.layout.viewlets import ViewletBase
from rer.newsletter.content.channel import Channel
from zope.annotation.interfaces import IAnnotations


KEY = 'rer.newsletter.message.details'


class MessageManagerViewlet(ViewletBase):

    def update(self):
        pass

    def _getChannel(self):
        return filter(lambda x: isinstance(x, Channel), aq_chain(self.context))

    def canManageNewsletter(self):

        if not self._getChannel():
            return False

        isEditor = 'Editor' in api.user.get_roles(obj=self.context)
        hasManageNewsletter = api.user.get_permissions(obj=self.context).get(
            'rer.newsletter: Manage Newsletter') and 'Gestore Newsletter' not \
            in api.user.get_roles(obj=self.context)
        if isEditor or hasManageNewsletter:
            return True
        else:
            return False

    def canSendMessage(self):

        if not self._getChannel():
            return False

        if (api.content.get_state(obj=self.context) == 'published'
                and api.user.get_permissions(obj=self.context).get(
                'rer.newsletter: Send Newsletter')):
            return True
        else:
            return False

    def messageSentDetails(self):
        annotations = IAnnotations(self.context)
        if KEY in annotations.keys():
            annotations = annotations[KEY]
            messages_details = []
            for k, v in annotations.iteritems():
                messages_details.append(v)
            return messages_details
        return None

    def render(self):
        return self.index()

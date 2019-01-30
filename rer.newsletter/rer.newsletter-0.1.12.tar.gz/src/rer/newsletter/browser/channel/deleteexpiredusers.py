# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from rer.newsletter import logger
from rer.newsletter.utils import storage
from zope.interface import alsoProvides


class DeleteExpiredUsersView(BrowserView):
    """ Delete expired users from channels """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.user_removed = 0

    def update_annotations(self, channel):
        expired_date = datetime.now()
        expired_time_token = self.context.portal_registry.get(
            'rer.newsletter.browser.settings.ISettingsSchema.expired_time_token',  # noqa
            None
        )

        annotations = storage(channel.getObject())
        for val in annotations.keys():
            creation_date = datetime.strptime(
                annotations[val]['creation_date'],
                '%d/%m/%Y %H:%M:%S')
            if creation_date + timedelta(hours=expired_time_token) < expired_date and not annotations[val]['is_active']:  # noqa
                del annotations[val]
                self.user_removed += 1

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        logger.info(u'START:Remove expired user from channels')

        pc = getToolByName(self.context, 'portal_catalog')  # noqa
        channels_brain = pc.unrestrictedSearchResults(
            {'portal_type': 'Channel'})

        map(lambda x: self.update_annotations(x), channels_brain)
        logger.info(u'DONE:Remove {0} expired user from channels'.format(
            self.user_removed))
        return True

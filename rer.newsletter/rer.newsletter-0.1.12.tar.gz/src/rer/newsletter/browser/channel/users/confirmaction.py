# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from rer.newsletter import _
from rer.newsletter.contentrules.events import SubscriptionEvent
from rer.newsletter.contentrules.events import UnsubscriptionEvent
from rer.newsletter.utility.channel import IChannelUtility
from rer.newsletter.utility.channel import OK
from rer.newsletter.utils import get_site_title
from zope.component import getUtility
from zope.event import notify


# disable CSRF
# from plone.protect.interfaces import IDisableCSRFProtection
# from zope.interface import alsoProvides


class ConfirmAction(BrowserView):

    def render(self):
        return self.index()

    def _sendGenericMessage(self, template, receiver, message, message_title):
        mail_template = self.context.restrictedTraverse(
            '@@{0}'.format(template)
        )

        parameters = {
            'header': self.context.header,
            'footer': self.context.footer,
            'style': self.context.css_style,
            'portal_name': get_site_title(),
            'channel_name': self.context.title,
        }

        mail_text = mail_template(**parameters)

        portal = api.portal.get()
        mail_text = portal.portal_transforms.convertTo(
            'text/mail', mail_text)

        response_email = None
        if self.context.sender_email:
            response_email = self.context.sender_email
        else:
            response_email = u'noreply@rer.it'

        # invio la mail ad ogni utente
        mail_host = api.portal.get_tool(name='MailHost')
        mail_host.send(
            mail_text.getData(),
            mto=receiver,
            mfrom=response_email,
            subject=message_title,
            charset='utf-8',
            msg_type='text/html'
        )

        return OK

    def __call__(self):
        secret = self.request.get('secret')
        action = self.request.get('action')

        response = None
        api_channel = getUtility(IChannelUtility)

        if action == u'subscribe':
            response, user = api_channel.activateUser(
                self.context.id_channel,
                secret=secret
            )
            # mandare mail di avvenuta conferma
            if response == OK:
                notify(SubscriptionEvent(self.context, user))
                self._sendGenericMessage(
                    template='activeuserconfirm_template',
                    receiver=user,
                    message='Messaggio di avvenuta iscrizione',
                    message_title='Iscrizione confermata'
                )
                status = _(
                    u'generic_activate_message_success',
                    default=u'Ti sei iscritto alla newsletter '
                    + self.context.title + ' del portale ' +
                    get_site_title()
                )

        elif action == u'unsubscribe':
            response, user = api_channel.deleteUser(
                self.context.id_channel,
                secret=secret
            )
            # mandare mail di avvenuta cancellazione
            if response == OK:
                notify(UnsubscriptionEvent(self.context, user))
                self._sendGenericMessage(
                    template='deleteuserconfirm_template',
                    receiver=user,
                    message='L\'utente è stato eliminato dal canale.',
                    message_title='Cancellazione avvenuta'
                )
                status = _(
                    u'generic_delete_message_success',
                    default=u'User Deleted.'
                )

        if response == OK:
            api.portal.show_message(
                message=status,
                request=self.request,
                type=u'info'
            )
        else:
            api.portal.show_message(
                message=u'Problems...{0}'.format(response),
                request=self.request,
                type=u'error'
            )

        return self.render()

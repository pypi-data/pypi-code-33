# -*- coding: utf-8 -*-
from rer.newsletter import _
from zope import schema
from zope.interface import Interface


class Notify(Interface):
    subject = schema.TextLine(
        title=_(u'Subject'),
        description=_(u'Subject of the message'),
        required=True
    )

    source = schema.TextLine(
        title=_(u'Sender email'),
        description=_(u'The email address that sends the email. If no email is'
                      ' provided here, it will use the portal from address.'),
        required=True
    )

    dest_addr = schema.TextLine(
        title=_(u'Receiver email'),
        description=_(
            u'The address where you want to send the e-mail message.'),
        required=True
    )

    message = schema.Text(
        title=_(u'Message'),
        description=_(u'Type in here the message that you want to mail. Some'
            u'defined content can be replaced: ${portal} will be replaced by the title'  # noqa
            u'of the portal. ${url} will be replaced by the URL of the newsletter.'  # noqa
            u'${channel} will be replaced by the newsletter channel name. ${subscriber} will be replaced by subscriber name.'),  # noqa
        required=True
    )


class INotifyOnSubscribe(Notify):
    """ notify on subscribe """


class INotifyOnUnsubscribe(Notify):
    """ notify on unsubscribe """

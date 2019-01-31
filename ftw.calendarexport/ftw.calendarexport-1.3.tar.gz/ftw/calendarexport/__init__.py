from Products.ATContentTypes.interfaces import ICalendarSupport
from zope.i18nmessageid import MessageFactory
import pkg_resources


_ = MessageFactory('ftw.calendarexport')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


EVENT_INTERFACES = [ICalendarSupport.__identifier__]

try:
    pkg_resources.get_distribution('plone.app.event')
except pkg_resources.DistributionNotFound:
    PLONE_APP_EVENTS_AVAILABLE = False
else:
    from plone.app.event.dx.interfaces import IDXEvent
    EVENT_INTERFACES.append(IDXEvent.__identifier__)
    PLONE_APP_EVENTS_AVAILABLE = True

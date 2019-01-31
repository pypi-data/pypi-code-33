from Acquisition import aq_inner
from ftw.calendarexport import PLONE_APP_EVENTS_AVAILABLE
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
from Products.ATContentTypes.browser.calendar import CalendarView, cachekey
from Products.ATContentTypes.interface.interfaces import ICalendarSupport
from Products.ATContentTypes.lib import calendarsupport as cs
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

if PLONE_APP_EVENTS_AVAILABLE:
    from plone.app.event.dx.interfaces import IDXEvent
    from plone.app.event.ical import construct_icalendar


class ExportEvents(ViewletBase):
    render = ViewPageTemplateFile('export.pt')

    def active(self):
        props = getToolByName(self.context, 'portal_properties').get(
            'calendarexport_properties', None)
        if not props:
            return False
        return props.getProperty('active')


class ExportICS(CalendarView):

    def update(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        uids = self.request.form.get('uids', [])
        self.events = catalog(UID=uids)
        if not uids:
            self.events = []

    @ram.cache(cachekey)
    def feeddata(self):
        header = cs.ICS_HEADER % dict(prodid=cs.PRODID)
        events = []
        for brain in self.events:
            obj = brain.getObject()
            event_data = ""

            if ICalendarSupport.providedBy(obj):
                event_data = obj.getICal()

            if PLONE_APP_EVENTS_AVAILABLE:
                if IDXEvent.providedBy(obj):
                    cal = construct_icalendar(obj, obj)
                    event = cal.subcomponents[0]
                    event_data = event.to_ical()

            events.append(event_data)

        return header + "".join(events) + cs.ICS_FOOTER

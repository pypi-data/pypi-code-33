from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.calendarexport.testing import FTW_CALENDAREXPORT_INTEGRATION_TESTING
from ftw.testing.staticuids import staticuid
from ftw.testing import freeze
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from pytz import UTC
from unittest2 import TestCase
import re


class TestCalendarExport(TestCase):

    layer = FTW_CALENDAREXPORT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_at_export(self):
        folder = create(Builder('folder').titled('testfolder'))
        event1 = create(Builder('at event')
                        .titled('event1')
                        .within(folder)
                        .having(startDate='2014-01-23 11:00',
                                endDate='2014-01-23 13:00'))
        event2 = create(Builder('at event')
                        .titled('event2')
                        .within(folder)
                        .having(startDate='2014-01-25 11:00',
                                endDate='2014-01-25 13:00'))

        view = folder.restrictedTraverse('export_ics')
        uids = []
        uids.append(event1.UID())
        uids.append(event2.UID())
        self.portal.REQUEST.form['uids'] = uids
        view()
        feeddata = view.feeddata()
        feed_list = feeddata.split('BEGIN:VEVENT')

        self.assertIn(
            'SUMMARY:event1\nDTSTART:20140123T100000Z\n'
            'DTEND:20140123T120000Z\nCLASS:PUBLIC\nEND:VEVENT\n',
            feed_list[1])
        self.assertIn(
            'SUMMARY:event2\nDTSTART:20140125T100000Z\n'
            'DTEND:20140125T120000Z\nCLASS:PUBLIC\nEND:VEVENT\nEND:VCALENDAR\n',
            feed_list[2])

    @staticuid()
    def test_dx_export(self):
        with freeze(datetime(2016, 7, 12, 11, 24, tzinfo=UTC)) as clock:
            folder = create(Builder('event folder'))
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            dayaftertomorrow = tomorrow + timedelta(days=1)
            event1 = create(Builder('event page')
                            .titled(u'Event One')
                            .within(folder)
                            .starting(today)
                            .ending(tomorrow))
            event2 = create(Builder('event page')
                            .titled(u'Event Two')
                            .within(folder)
                            .starting(tomorrow)
                            .ending(dayaftertomorrow))

            view = folder.restrictedTraverse('export_ics')
            uids = list()
            uids.append(event1.UID())
            uids.append(event2.UID())
            self.portal.REQUEST.form['uids'] = uids
            view()
            feeddata = view.feeddata().replace('\r\n', '\n')

            events = re.findall('BEGIN:VEVENT\n(.*?)\nEND:VEVENT',
                                feeddata, flags=re.DOTALL)
            # convert vevent into dict
            events = [{kv.split(':', 1)[0]: kv.split(':', 1)[1] for kv in
                      event.split('\n')} for event in events]

            self.assertEqual(
                [{'CREATED;VALUE=DATE-TIME': '20160712T102400Z',
                  'DTEND;TZID=Etc/Greenwich;VALUE=DATE-TIME': '20160713T112400',
                  'DTSTAMP;VALUE=DATE-TIME': '20160712T112400Z',
                  'DTSTART;TZID=Etc/Greenwich;VALUE=DATE-TIME':
                      '20160712T112400',
                  'LAST-MODIFIED;VALUE=DATE-TIME': '20160712T102400Z',
                  'SUMMARY': 'Event One',
                  'UID': 'testdxexport00000000000000000003',
                  'URL': 'http://nohost/plone/ftw-events-eventfolder/event'
                         '-one'},
                 {'CREATED;VALUE=DATE-TIME': '20160712T102400Z',
                  'DTEND;TZID=Etc/Greenwich;VALUE=DATE-TIME': '20160714T112400',
                  'DTSTAMP;VALUE=DATE-TIME': '20160712T112400Z',
                  'DTSTART;TZID=Etc/Greenwich;VALUE=DATE-TIME':
                      '20160713T112400',
                  'LAST-MODIFIED;VALUE=DATE-TIME': '20160712T102400Z',
                  'SUMMARY': 'Event Two',
                  'UID': 'testdxexport00000000000000000004',
                  'URL': 'http://nohost/plone/ftw-events-eventfolder/event'
                         '-two'}],
                events
            )

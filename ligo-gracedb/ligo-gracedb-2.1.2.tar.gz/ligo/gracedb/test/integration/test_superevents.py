# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function
from builtins import map
from collections import defaultdict
import datetime
import os
import six
from six.moves import range
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from ligo.gracedb.rest import GraceDb
from ligo.gracedb.exceptions import HTTPError
from .base import TestGraceDb


class TestSuperevents(TestGraceDb):
    """Set of unit tests for superevent capabilities of gracedb-client"""

    @classmethod
    def setUpClass(cls):
        # Create an event for testing so we don't have to create a lot of
        # events for all of the unit tests.
        super(TestSuperevents, cls).setUpClass()

        # Create some useful events
        eventFile = os.path.join(cls.TEST_DATA_DIR, "cbc-lm.xml")
        cls._events = []
        for i in range(8):
            event = cls._gracedb.createEvent("Test", "gstlal",
                eventFile, "LowMass").json()
            cls._events.append(event['graceid'])

        # Create one useful superevent
        superevent = cls._gracedb.createSuperevent(1, 2, 3,
            preferred_event=cls._events[0], category='Test').json()
        cls.superevent = superevent
        cls.superevent_id = superevent['superevent_id']

    def test_superevent_categories(self):
        """Verify that superevent categories are available"""
        self.assertIsNotNone(self._gracedb.superevent_categories)

    def test_basic_creation(self):
        """Basic superevent creation"""
        response = self._gracedb.createSuperevent(0, 1, 2,
            preferred_event=self._events[1], category='Test')

        # Get response data
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test superevent attributes
        self.assertEqual(data['t_start'], 0)
        self.assertEqual(data['t_0'], 1)
        self.assertEqual(data['t_end'], 2)
        self.assertEqual(data['preferred_event'], self._events[1])
        self.assertEqual(data['category'], 'Test')

        # Try creation again with same preferred event - expect to fail
        with self.assertRaises(HTTPError):
            response = self._gracedb.createSuperevent(10, 11, 12,
                preferred_event=self._events[1], category="Test")

    def test_creation_with_events(self):
        """Create superevent with additional events"""
        response = self._gracedb.createSuperevent(0, 1, 2,
            preferred_event=self._events[2], category='Test',
            events=self._events[3:5])

        # Get response data
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test preferred event's graceid
        self.assertEqual(data['preferred_event'], self._events[2])

        # Test graceids of gw_events
        for ev in self._events[2:5]:
            self.assertIn(ev, data['gw_events'])

    def test_creation_with_labels(self):
        """Create superevent with labels"""
        label = self._gracedb.allowed_labels[0]
        response = self._gracedb.createSuperevent(0, 1, 2,
            preferred_event=self._events[5],
            labels=[label], category="Test")

        # Get response data
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test superevent attributes
        self.assertEqual(data['t_start'], 0)
        self.assertEqual(data['t_0'], 1)
        self.assertEqual(data['t_end'], 2)
        self.assertEqual(data['preferred_event'], self._events[5])
        self.assertEqual(data['category'], 'Test')
        self.assertIn(label, data['labels'])

    @mock.patch.object(GraceDb, 'request')
    @mock.patch.object(GraceDb, 'allowed_labels', new_callable=mock.PropertyMock)
    def test_creation_with_bad_labels(self, mock_allowed_labels, mock_request):
        """Try to create superevent with non-existent labels"""
        mock_allowed_labels.return_value = ['GOOD_LABEL']

        bad_labels = ['bad', ['BAD_LABEL']]
        for label in bad_labels:
            with self.assertRaises(NameError):
                r = self._gracedb.createSuperevent(0, 1, 2,
                    preferred_event=self._events[6],
                    labels=label, category='Test')

        bad_labels2 = [1, True]
        for label2 in bad_labels2:
            with self.assertRaises(TypeError):
                r = self._gracedb.createSuperevent(0, 1, 2,
                    preferred_event=self._events[6],
                    labels=label2, category='Test')
        mock_request.assert_not_called()

    @mock.patch.object(GraceDb, 'post')
    def test_creation_categories(self, mock_post):
        """Try to create superevent with a variety of good categories"""
        good_categories = ['TeSt', 'T', 'productioN', 'p', 'MdC', 'M']
        for category in good_categories: 
            r = self._gracedb.createSuperevent(0, 1, 2,
                preferred_event=self._events[6],
                category=category)

            # Check calls to post to see that category was adjusted properly
            call_kwargs = mock_post.call_args[1]
            self.assertEqual(category[0].upper(),
                call_kwargs['body']['category'])

    @mock.patch.object(GraceDb, 'post')
    def test_creation_with_bad_categories(self, mock_post):
        """Try to create superevent with bad category"""
        with self.assertRaises(NameError):
            r = self._gracedb.createSuperevent(0, 1, 2,
                preferred_event=self._events[6],
                labels=['BAD_LABEL'], category='BAD_CATEGORY')

    def test_retrieval(self):
        """Retrieve a superevent"""
        response = self._gracedb.superevent(self.superevent_id)
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 200)

        # Test superevent attributes
        self.assertEqual(data['t_start'], 1)
        self.assertEqual(data['t_0'], 2)
        self.assertEqual(data['t_end'], 3)
        self.assertEqual(data['preferred_event'], self._events[0])
        self.assertEqual(data['category'], 'Test')

    def test_update(self):
        """Test update of superevent"""
        # Get original data for superevent
        response = self._gracedb.superevent(self.superevent_id)
        original_data = response.json()

        # Update the superevent
        response = self._gracedb.updateSuperevent(self.superevent_id,
            11, 12, 13, preferred_event=self._events[6])
        data = response.json()

        # Check response status
        self.assertEqual(response.status, 200)

        # Test superevent attributes
        self.assertEqual(data['t_start'], 11)
        self.assertEqual(data['t_0'], 12)
        self.assertEqual(data['t_end'], 13)
        self.assertEqual(data['preferred_event'], self._events[6])
        self.assertEqual(data['category'], 'Test')

        # Test that old and new preferred event are in gw_events
        self.assertIn(original_data['preferred_event'], data['gw_events'])
        self.assertIn(self._events[6], data['gw_events'])

    def test_event_addition_and_removal(self):
        """Add/remove events to/from a superevent"""
        event = self._events[7]

        # Get initial superevent data
        initial_superevent_data = self._gracedb.superevent(
            self.superevent_id).json()

        # Test for event presence
        self.assertNotIn(event, initial_superevent_data['gw_events'])

        # Add event
        response = self._gracedb.addEventToSuperevent(self.superevent_id,
            event)
        added_event_data = response.json()
        updated_superevent_data = self._gracedb.superevent(
            self.superevent_id).json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test for event presense
        self.assertIn(event, added_event_data['graceid'])
        self.assertIn(event, updated_superevent_data['gw_events'])

        # Try to add event again (expect error)
        with self.assertRaises(HTTPError):
            response = self._gracedb.addEventToSuperevent(
                self.superevent_id, event)

        # Remove event
        response = self._gracedb.removeEventFromSuperevent(
            self.superevent_id, event)
        updated_superevent_data = self._gracedb.superevent(
            self.superevent_id).json()

        # Test response
        self.assertEqual(response.status, 204)

        # Test for event presence
        self.assertNotIn(event, updated_superevent_data['gw_events'])

        # Try to remove event again (expect error)
        with self.assertRaises(HTTPError):
            response = self._gracedb.removeEventFromSuperevent(
                self.superevent_id, event)

        # Try to remove preferred event (expect error)
        with self.assertRaises(HTTPError):
            response = self._gracedb.removeEventFromSuperevent(
                self.superevent_id, updated_superevent_data['preferred_event'])

    def test_search(self):
        """Test superevents search"""
        # Basic search test - get all superevents and check the first one
        for superevent in self._gracedb.superevents():
            self.assertTrue('superevent_id' in superevent)
            break

        # Search for superevent by ID
        response = self._gracedb.superevents(self.superevent_id)
        results_list = list(response)
        self.assertEqual(len(results_list), 1)
        self.assertEqual(results_list[0]['superevent_id'], self.superevent_id)

    def test_confirm_as_gw(self):
        """Confirm a superevent as a GW"""
        # Make sure this is a non-GW type
        self.assertIsNone(self.superevent['gw_id'])
        self.assertFalse(self.superevent_id.startswith('TGW') or 
            'GW' in self.superevent_id[:3])

        # Confirm as gw
        response = self._gracedb.confirm_superevent_as_gw(self.superevent_id)
        confirmed_data = response.json()

        # Test response status
        self.assertEqual(response.status, 200)

        # Check new ID in response
        gw_id = confirmed_data['gw_id']
        self.assertTrue(gw_id.startswith('TGW') or 'GW' in gw_id[:3])

        # Try to update again
        with self.assertRaises(HTTPError):
            response = self._gracedb.confirm_superevent_as_gw(
                self.superevent_id)

        # Get data using "old" (TS-type) and "new" (TGW-type) IDs
        initial_id_data = self._gracedb.superevent(self.superevent_id).json()
        gw_id_data = self._gracedb.superevent(gw_id).json()

        # Compare results
        self.assertEqual(initial_id_data, gw_id_data)
        self.assertEqual(initial_id_data['superevent_id'],
            self.superevent['superevent_id'])
        self.assertEqual(gw_id_data['superevent_id'],
            self.superevent['superevent_id'])
        self.assertEqual(gw_id, gw_id_data['gw_id'])

    def test_log_creation_and_retrieval(self):
        """Create a log and retrieve it"""
        # Write log
        msg = 'test message'
        response = self._gracedb.writeLog(self.superevent_id, msg)
        data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test data
        self.assertEqual(data['comment'], msg)

        # Retrieve superevent log
        log_N = data['N']
        response = self._gracedb.logs(self.superevent_id, log_N)
        log_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test data
        self.assertEqual(log_data['N'], log_N)
        self.assertEqual(log_data['comment'], msg)

    def test_log_creation_and_retrieval_with_file(self):
        # Write log
        msg = 'test message'
        upload = os.path.join(self.TEST_DATA_DIR, "test_file.txt")
        response = self._gracedb.writeLog(self.superevent_id, msg,
            filename=upload)
        data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test data
        self.assertEqual(data['comment'], msg)
        self.assertEqual(data['filename'], os.path.basename(upload))
        self.assertEqual(data['file_version'], 0)

        # Retrieve superevent log
        log_N = data['N']
        response = self._gracedb.logs(self.superevent_id, log_N)
        log_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test data
        self.assertEqual(log_data['N'], log_N)
        self.assertEqual(log_data['comment'], msg)
        self.assertEqual(log_data['filename'], os.path.basename(upload))
        self.assertEqual(log_data['file_version'], 0)

        # Upload a second file
        response = self._gracedb.writeLog(self.superevent_id, msg,
            filename=upload)
        data2 = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test data
        self.assertEqual(data2['comment'], msg)
        self.assertEqual(data2['filename'], os.path.basename(upload))
        self.assertEqual(data2['file_version'], 1)

        # Get files
        response = self._gracedb.files(self.superevent_id)
        file_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test file list (2 versioned + 1 non-versioned)
        self.assertEqual(len(file_data), 3)

        # Get one file
        response = self._gracedb.files(self.superevent_id,
            os.path.basename(upload))

        # Test response status
        self.assertEqual(response.status, 200)

        # Test file contents
        file_from_server = response.read()
        file_handler = open(upload, 'rb')
        file_from_disk = file_handler.read()
        file_handler.close()
        self.assertEqual(file_from_server, file_from_disk)

    def test_log_creation_and_retrieval_with_tag(self):
        """Create a superevent log with a tag"""
        # Write log
        tags = ['sky_loc', 'em_follow']
        msg = 'test message'
        upload = os.path.join(self.TEST_DATA_DIR, "test_file.txt")
        response = self._gracedb.writeLog(self.superevent_id, msg,
            tag_name=tags)
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test response data
        # We use six here since assertItemsEqual in Python 2.7 is
        # called assertCountEqual in Python 3.3+
        six.assertCountEqual(self, tags, data['tag_names'])
        self.assertEqual(data['comment'], msg)

    def test_log_tag_and_untag(self):
        """Tag and untag a superevent log"""
        # Write log
        msg = 'test message'
        response = self._gracedb.writeLog(self.superevent_id, msg)
        data = response.json()

        # Test response status
        self.assertEqual(response.status, 201)

        # Test response data
        self.assertEqual(data['comment'], msg)
        self.assertFalse(data['tag_names']) # empty

        # Add tag
        tag = 'sky_loc'
        response = self._gracedb.addTag(self.superevent_id, data['N'], tag)
        tag_data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test tag data
        self.assertEqual(tag, tag_data['name'])

        # Get superevent log
        response = self._gracedb.logs(self.superevent_id, data['N'])
        log_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test log tags
        # We use six here since assertItemsEqual in Python 2.7 is
        # called assertCountEqual in Python 3.3+
        six.assertCountEqual(self, [tag], log_data['tag_names'])

        # Remove tag from log
        response = self._gracedb.removeTag(self.superevent_id, data['N'], tag)
        untag_data = response.json()

        # Test response
        self.assertEqual(response.status, 204)

        # Get superevent log again
        response = self._gracedb.logs(self.superevent_id, data['N'])
        log_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test log data
        self.assertNotIn(tag, log_data['tag_names'])
        self.assertEqual([], log_data['tag_names'])

    def test_labels(self):
        """Add, remove, list, retrieve labels"""
        label = self._gracedb.allowed_labels[0]

        # Add label to superevent
        response = self._gracedb.writeLabel(self.superevent_id, label)
        data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test response data
        self.assertEqual(data['name'], label)

        # Try to add label again
        with self.assertRaises(HTTPError):
            response = self._gracedb.writeLabel(self.superevent_id, label)

        # Get superevent
        response = self._gracedb.superevent(self.superevent_id)
        data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test response data
        self.assertEqual([label], data['labels'])

        # Remove label
        response = self._gracedb.removeLabel(self.superevent_id, label)

        # Test response
        self.assertEqual(response.status, 204)

        # Try to remove label again
        with self.assertRaises(HTTPError):
            response = self._gracedb.removeLabel(self.superevent_id, label)

    def test_emobservations(self):
        """Add, list, retrieve emobservations"""

        # Create an emobservation
        emgroup = self._gracedb.em_groups[0]
        ra_list = [1, 2, 3, 4]
        ra_width_list = [0.5]*len(ra_list)
        dec_list = [5, 6, 7, 8]
        dec_width_list = [0.7]*len(dec_list)
        now = datetime.datetime.now()
        start_time_list = list(map(lambda i:
            (now + datetime.timedelta(seconds=i)).isoformat(), [0, 1, 2, 3]))
        duration_list = [1]*len(start_time_list)
        comment = "test comment"
        response = self._gracedb.writeEMObservation(self.superevent_id,
            emgroup, ra_list, ra_width_list, dec_list, dec_width_list,
            start_time_list, duration_list, comment=comment)
        data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test response data - we don't test values like ra, dec,
        # ra_width, dec_width for the emobservation itself because they
        # are calculated following some formula on the server, which we don't
        # want to implement here
        self.assertEqual(data['comment'], comment)
        self.assertEqual(data['group'], emgroup)
        self.assertEqual(len(data['footprints']), len(ra_list))
        for emf in data['footprints']:
            N = emf['N']
            self.assertEqual(emf['ra'], ra_list[N-1])
            self.assertEqual(emf['dec'], dec_list[N-1])
            self.assertEqual(emf['raWidth'], ra_width_list[N-1])
            self.assertEqual(emf['decWidth'], dec_width_list[N-1])
            self.assertEqual(emf['exposure_time'], duration_list[N-1])
            # Don't compare start times; would be super painful due to string
            # casting and time zones

        # Get list of emobservations
        response = self._gracedb.emobservations(self.superevent_id)
        list_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test response data
        self.assertEqual(len(list_data['observations']), 1)

        # Retrieve individual emobservation
        response = self._gracedb.emobservations(self.superevent_id,
            data['N'])
        ret_data = response.json()

        # Test response
        self.assertEqual(response.status, 200)

        # Test response data
        self.assertEqual(ret_data['comment'], comment)
        self.assertEqual(ret_data['group'], emgroup)
        self.assertEqual(len(ret_data['footprints']), len(ra_list))
        for emf in ret_data['footprints']:
            N = emf['N']
            self.assertEqual(emf['ra'], ra_list[N-1])
            self.assertEqual(emf['dec'], dec_list[N-1])
            self.assertEqual(emf['raWidth'], ra_width_list[N-1])
            self.assertEqual(emf['decWidth'], dec_width_list[N-1])
            self.assertEqual(emf['exposure_time'], duration_list[N-1])

    def test_voevents(self):
        """Add, list, retrieve voevents"""

        # Create preliminary voevent
        pr_voevent = {
            'skymap_type': None,
            'skymap_filename': None,
            'internal': True,
            'hardware_inj': False,
            'open_alert': False,
            'CoincComment': False,
            'ProbHasNS': 0.1,
            'ProbHasRemnant': 0.9,
            'BNS': 0.2,
            'NSBH': 0.3,
            'BBH': 0.4,
            'Terrestrial': 0.5,
        }
        response = self._gracedb.createVOEvent(self.superevent_id, 'PR',
            **pr_voevent)
        pr_data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test data - most of it is in the file text, so we don't
        # get that and check it
        self.assertEqual(pr_data['voevent_type'], 'PR')

        # Upload fake skymap files
        filename = os.path.join(self.TEST_DATA_DIR, "test_file.txt")
        filename2 = os.path.join(self.TEST_DATA_DIR, "test_file2.txt")
        self._gracedb.writeLog(self.superevent_id, 'fake skymap',
            filename=filename)
        self._gracedb.writeLog(self.superevent_id, 'fake skymap image',
            filename=filename2)

        # Try to create another one
        up_voevent = {
            'skymap_type': 'update',
            'skymap_filename': os.path.basename(filename),
            'internal': False,
            'hardware_inj': False,
            'open_alert': False,
            'CoincComment': False,
            'ProbHasNS': 0.2,
            'ProbHasRemnant': 0.9,
            'BNS': 0.2,
            'NSBH': 0.3,
            'BBH': 0.4,
            'Terrestrial': 0.5,
        }
        response = self._gracedb.createVOEvent(self.superevent_id, 'UP',
            **up_voevent)
        up_data = response.json()

        # Test response
        self.assertEqual(response.status, 201)

        # Test data - most of it is in the file text, so we don't
        # get that and check it
        self.assertEqual(up_data['voevent_type'], 'UP')

        # Get list of voevents and check it
        response = self._gracedb.voevents(self.superevent_id)
        list_data = response.json()

        # Check response
        self.assertEqual(response.status, 200)

        # Check response data
        self.assertEqual(len(list_data['voevents']), 2)

        # Retrieve first voevent
        response = self._gracedb.voevents(self.superevent_id, pr_data['N'])
        ret_data = response.json()

        # Check response
        self.assertEqual(response.status, 200)

        # Check response data
        self.assertEqual(ret_data['voevent_type'], 'PR')

    def test_signoffs(self):
        """Create, update, delete, and retrieve signoffs"""
        # We have to test advocate signoffs only, because operator signoff
        # groups are assigned based on IP address.

        # Add "signoff requested" label to superevent
        response = self._gracedb.writeLabel(self.superevent_id, 'ADVREQ')
        self.assertEqual(response.status, 201)

        # Create a signoff
        response = self._gracedb.create_signoff(self.superevent_id, 'ADV',
            'OK', "looks good")
        ret_data = response.json()
        self.assertEqual(response.status, 201)
        self.assertEqual(ret_data['status'], 'OK')
        self.assertEqual(ret_data['comment'], 'looks good')
        self.assertEqual(ret_data['instrument'], '')
        self.assertEqual(ret_data['signoff_type'], 'ADV')

        # Check signoff from API signoff list
        response = self._gracedb.signoffs(self.superevent_id)
        self.assertEqual(response.status, 200)
        ret_data = response.json()
        self.assertEqual(len(ret_data['signoffs']), 1)
        signoff = ret_data['signoffs'][0]
        self.assertEqual(signoff['status'], 'OK')
        self.assertEqual(signoff['comment'], 'looks good')
        self.assertEqual(signoff['instrument'], '')
        self.assertEqual(signoff['signoff_type'], 'ADV')

        # Test retrieving the same signoff directly rather than from
        # the list of signoffs for this superevent
        response = self._gracedb.signoffs(self.superevent_id,
            signoff_type='ADV')
        self.assertEqual(response.status, 200)
        signoff = response.json()
        self.assertEqual(signoff['status'], 'OK')
        self.assertEqual(signoff['comment'], 'looks good')
        self.assertEqual(signoff['instrument'], '')
        self.assertEqual(signoff['signoff_type'], 'ADV')

        # Check label status
        response = self._gracedb.labels(self.superevent_id)
        ret_data = response.json()
        self.assertEqual(response.status, 200)
        label_names = [l['name'] for l in ret_data['labels']]
        self.assertNotIn('ADVREQ', label_names)
        self.assertIn('ADVOK', label_names)
        self.assertNotIn('ADVNO', label_names)

        # Update signoff
        response = self._gracedb.update_signoff(self.superevent_id, 'ADV',
            status='NO', comment='not OK')
        ret_data = response.json()
        self.assertEqual(response.status, 200)
        self.assertEqual(ret_data['status'], 'NO')
        self.assertEqual(ret_data['comment'], 'not OK')
        self.assertEqual(ret_data['instrument'], '')
        self.assertEqual(ret_data['signoff_type'], 'ADV')

        # Check signoff from API
        response = self._gracedb.signoffs(self.superevent_id)
        ret_data = response.json()
        self.assertEqual(response.status, 200)
        self.assertEqual(len(ret_data['signoffs']), 1)
        signoff = ret_data['signoffs'][0]
        self.assertEqual(signoff['status'], 'NO')
        self.assertEqual(signoff['comment'], 'not OK')
        self.assertEqual(signoff['instrument'], '')
        self.assertEqual(signoff['signoff_type'], 'ADV')

        # Check label status
        response = self._gracedb.labels(self.superevent_id)
        ret_data = response.json()
        self.assertEqual(response.status, 200)
        label_names = [l['name'] for l in ret_data['labels']]
        self.assertNotIn('ADVREQ', label_names)
        self.assertNotIn('ADVOK', label_names)
        self.assertIn('ADVNO', label_names)

        # Delete signoff
        response = self._gracedb.delete_signoff(self.superevent_id, 'ADV')
        self.assertEqual(response.status, 204)
        ret_data = response.json()
        self.assertEqual(ret_data, {})

        # Check signoff from API
        response = self._gracedb.signoffs(self.superevent_id)
        self.assertEqual(response.status, 200)
        ret_data = response.json()
        self.assertEqual(len(ret_data['signoffs']), 0)

        # Check label status
        response = self._gracedb.labels(self.superevent_id)
        ret_data = response.json()
        self.assertEqual(response.status, 200)
        label_names = [l['name'] for l in ret_data['labels']]
        self.assertIn('ADVREQ', label_names)
        self.assertNotIn('ADVOK', label_names)
        self.assertNotIn('ADVNO', label_names)

    def test_permissions(self):
        """Retrieve and modify permissions"""

        # Get permissions for superevent, should be blank
        response = self._gracedb.permissions(self.superevent_id)
        self.assertEqual(response.status, 200)
        data = response.json()
        self.assertEqual(data['permissions'], [])

        # Expose superevent to public
        response = self._gracedb.modify_permissions(self.superevent_id,
            'expose')
        self.assertEqual(response.status, 200)
        data = response.json()
        self.assertEqual(len(data), 3)
        # Compile response data into dict with group name keys
        group_perms = defaultdict(list)
        for p in data:
            group_perms[p['group']].append(p['permission'])
        # Check contents
        for group, perms in six.iteritems(group_perms):
            if (group == 'public_users'):
                self.assertEqual(len(perms), 1)
                self.assertIn('view_superevent', perms)
            elif (group == 'gw-astronomy:LV-EM:Observers'):
                self.assertEqual(len(perms), 2)
                self.assertIn('view_superevent', perms)
                self.assertIn('annotate_superevent', perms)

        # Test permissions list
        response = self._gracedb.permissions(self.superevent_id)
        self.assertEqual(response.status, 200)
        data = response.json()['permissions']
        self.assertEqual(len(data), 3)
        # Compile response data into dict with group name keys
        group_perms = defaultdict(list)
        for p in data:
            group_perms[p['group']].append(p['permission'])
        # Check contents
        for group, perms in six.iteritems(group_perms):
            if (group == 'public_users'):
                self.assertEqual(len(perms), 1)
                self.assertIn('view_superevent', perms)
            elif (group == 'gw-astronomy:LV-EM:Observers'):
                self.assertEqual(len(perms), 2)
                self.assertIn('view_superevent', perms)
                self.assertIn('annotate_superevent', perms)

        # Hide superevent from public
        response = self._gracedb.modify_permissions(self.superevent_id, 'hide')
        self.assertEqual(response.status, 200)
        data = response.json()
        self.assertEqual(data, [])


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)

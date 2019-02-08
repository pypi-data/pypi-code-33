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
import os
import six
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from ligo.gracedb.rest import GraceDb

@mock.patch.object(GraceDb, 'set_up_connector')
class TestClientSetup(unittest.TestCase):
    """Set of unit tests for client constructor"""

    def test_provide_x509_cert_and_key(self, mock_set_up_connector):
        """Test providing X509 cert and key to constructor"""
        # Setup
        cert_file = '/tmp/cert_file'
        key_file = '/tmp/key_file'

        # Initialize client
        g = GraceDb(cred=(cert_file, key_file))

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], cert_file)
        self.assertEqual(g.credentials['key_file'], key_file)
        self.assertEqual(g.auth_type, 'x509')

    def test_provide_x509_proxy(self, mock_set_up_connector):
        """Test providing X509 combined proxy to constructor"""
        # Setup
        combined_proxy_file = '/tmp/proxy_file'

        # Initialize client
        g = GraceDb(cred=combined_proxy_file)

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], combined_proxy_file)
        self.assertEqual(g.credentials['key_file'], combined_proxy_file)
        self.assertEqual(g.auth_type, 'x509')

    def test_provide_username_and_password(self, mock_set_up_connector):
        """Test providing username and password to constructor"""
        # Setup
        username = 'user'
        password = 'pw'

        # Initialize client
        g = GraceDb(username=username, password=password)

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['username'], username)
        self.assertEqual(g.credentials['password'], password)
        self.assertEqual(g.auth_type, 'basic')

    def test_provide_username_only(self, mock_set_up_connector):
        """Test providing only username to constructor"""
        # Setup
        username = 'user'

        # Initialize client
        with six.assertRaisesRegex(self, RuntimeError,
            'Must provide both username AND password for basic auth.'):
            g = GraceDb(username=username)

    def test_provide_password_only(self, mock_set_up_connector):
        """Test providing only password to constructor"""
        # Setup
        password = 'pw'

        # Initialize client
        with six.assertRaisesRegex(self, RuntimeError,
            'Must provide both username AND password for basic auth.'):
            g = GraceDb(password=password)

    def test_provide_all_creds(self, mock_set_up_connector):
        """
        Test providing X509 credentials and username/password to constructor
        """
        # Setup
        cert_file = '/tmp/cert_file'
        key_file = '/tmp/key_file'
        username = 'user'
        password = 'pw'

        # Initialize client
        g = GraceDb(cred=(cert_file, key_file), username=username,
            password=password)

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], cert_file)
        self.assertEqual(g.credentials['key_file'], key_file)
        self.assertEqual(g.auth_type, 'x509')

    @mock.patch.object(GraceDb, '_find_x509_credentials')
    def test_x509_cred_lookup(self, mock_find_x509, mock_set_up_connector):
        """Test lookup of X509 credentials"""
        # Setup
        cert_file = '/tmp/cert_file'
        key_file = '/tmp/key_file'
        mock_find_x509.return_value = (cert_file, key_file)

        # Initialize client
        g = GraceDb()

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], cert_file)
        self.assertEqual(g.credentials['key_file'], key_file)
        self.assertEqual(g.auth_type, 'x509')

    def test_x509_cred_lookup_cert_key_envvars(self, mock_set_up_connector):
        """Test lookup of X509 credentials from cert and key env variables"""
        # Setup
        cert_file = '/tmp/cert_file'
        key_file = '/tmp/key_file'

        # Initialize client
        with mock.patch.dict(os.environ, {'X509_USER_CERT': cert_file,
            'X509_USER_KEY': key_file}):

            # Initialize client
            g = GraceDb()

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], cert_file)
        self.assertEqual(g.credentials['key_file'], key_file)
        self.assertEqual(g.auth_type, 'x509')

    def test_x509_cred_lookup_proxy_envvar(self, mock_set_up_connector):
        """Test lookup of X509 credentials from proxy env variable"""
        # Setup
        proxy_file = '/tmp/proxy_file'

        with mock.patch.dict(os.environ, {'X509_USER_PROXY': proxy_file}):
            # Initialize client
            g = GraceDb()

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['cert_file'], proxy_file)
        self.assertEqual(g.credentials['key_file'], proxy_file)
        self.assertEqual(g.auth_type, 'x509')

    @mock.patch.object(GraceDb, '_find_x509_credentials')
    @mock.patch('ligo.gracedb.rest.safe_netrc')
    def test_basic_auth_cred_lookup(self, mock_netrc, mock_find_x509,
        mock_set_up_connector):
        """Test lookup of basic auth credentials from .netrc file"""
        # Force lookup to not find any X509 credentials
        mock_find_x509.return_value = None
        # Set up credentials and mock_netrc return
        fake_creds = {
            'machine': 'fake.com',
            'login': 'fake_user',
            'password': 'fake_password',
        }
        mock_netrc().authenticators.return_value = (fake_creds['login'],
            None, fake_creds['password'])

        # Initialize client
        g = GraceDb('https://{0}/api/'.format(fake_creds['machine']))

        # Check credentials
        self.assertEqual(len(g.credentials), 2)
        self.assertEqual(g.credentials['username'], fake_creds['login'])
        self.assertEqual(g.credentials['password'], fake_creds['password'])
        self.assertEqual(g.auth_type, 'basic')

    @mock.patch.object(GraceDb, '_find_x509_credentials')
    @mock.patch('ligo.gracedb.rest.safe_netrc')
    def test_no_creds(self, mock_netrc, mock_find_x509, mock_set_up_connector):
        """Test providing no credentials and having none to look up"""
        # Force lookup to not find any X509 credentials
        mock_find_x509.return_value = None
        # Force lookup to not find credentials in a .netrc file
        mock_netrc().authenticators.return_value = None

        # Initialize client
        g = GraceDb()

        # Check credentials
        self.assertEqual(len(g.credentials), 0)
        self.assertIsNone(g.auth_type)

    @mock.patch.object(GraceDb, '_find_x509_credentials')
    @mock.patch('ligo.gracedb.rest.safe_netrc')
    def test_no_creds_fail_noauth(self, mock_netrc, mock_find_x509,
        mock_set_up_connector):
        """
        Test providing no credentials and having none to look up, but
        requiring auth
        """
        # Force lookup to not find any X509 credentials
        mock_find_x509.return_value = None
        # Force lookup to not find credentials in a .netrc file
        mock_netrc().authenticators.return_value = None

        # Initialize client
        with six.assertRaisesRegex(self, RuntimeError,
            'No authentication credentials found'):
            g = GraceDb(fail_if_noauth=True)

    def test_force_noauth(self, mock_set_up_connector):
        """Test forcing no authentication, even with X509 certs available"""
        # Setup
        cert_file = '/tmp/cert_file'
        key_file = '/tmp/key_file'

        # Initialize client
        with mock.patch.dict(os.environ, {'X509_USER_CERT': cert_file,
            'X509_USER_KEY': key_file}):

            # Initialize client
            g = GraceDb(force_noauth=True)

        # Check credentials
        self.assertEqual(len(g.credentials), 0)
        self.assertIsNone(g.auth_type)

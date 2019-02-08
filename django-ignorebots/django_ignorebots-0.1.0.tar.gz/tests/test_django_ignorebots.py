#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import django
from django.core import mail
from django.test import Client, override_settings, SimpleTestCase

from django_ignorebots import ALL_URLS

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


@override_settings(
    IGNORABLE_404_URLS=ALL_URLS,
)
class TestIgnoreBotsURLS(SimpleTestCase):
    """Tests for `django_ignorebots` package."""

    def setUp(self):
        self.client = Client(
            HTTP_REFERER='http://example.com',
        )

    def test_unignored_url(self):
        """Test a 404 URL that shouldn't be ignored."""
        self.assertEqual(len(mail.outbox), 0)
        self.client.get('/dont-ignore-me')
        self.assertEqual(len(mail.outbox), 1)

    def test_ignored_urls(self):
        """Test known bot 404 URLs that should be ignored."""
        urls = [
            '/.bitcoin/wallet.dat',
            '/axis2/axis2-admin/login',
            '/backup/bitcoin/',
            '/backup/bitcoin/wallet.dat',
            '/backup/wallet.dat',
            '/bitcoin/',
            '/bitcoin/backup/wallet.dat',
            '/blog/wp-includes/wlwmanifest.xml',
            '/cms/wp-includes/wlwmanifest.xml',
            '/site/wp-admin/',
            '/site/wp-includes/wlwmanifest.xml',
            '/wordpress/wp-admin/',
            '/wordpress/wp-includes/wlwmanifest.xml',
            '/wp/wp-includes/wlwmanifest.xml',
            '/wp-admin/',
            '/wp-content/plugins/dzs-zoomsounds/admin/upload.php',
            '/wp-content/plugins/estatik/readme.txt',
            '/wp-content/plugins/wp-vertical-gallery/readme.txt',
            '/wp-content/plugins/wp-formgenerator/changelog.txt',
            '/wp-includes/wlwmanifest.xml',
            '/wp-login.php',
            '/xmlrpc.php',
        ]
        for url in urls:
            with self.subTest(msg='Testing known bot url', url=url):
                mail.outbox.clear()
                self.client.get(url)
                self.assertEqual(len(mail.outbox), 0)

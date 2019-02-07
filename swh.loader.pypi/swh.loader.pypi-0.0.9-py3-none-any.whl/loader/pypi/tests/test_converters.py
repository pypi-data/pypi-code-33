# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from unittest import TestCase

from swh.loader.pypi.converters import EMPTY_AUTHOR, author

from .common import WithProjectTest


class Test(WithProjectTest):
    def test_info(self):
        actual_info = self.project.info()

        expected_info = {
            'home_page': self.data['info']['home_page'],
            'description': self.data['info']['description'],
            'summary': self.data['info']['summary'],
            'license': self.data['info']['license'],
            'package_url': self.data['info']['package_url'],
            'project_url': self.data['info']['project_url'],
            'upstream': self.data['info']['project_urls']['Homepage'],
        }

        self.assertEqual(expected_info, actual_info)

    def test_author(self):
        info = self.data['info']
        actual_author = author(info)

        name = info['author'].encode('utf-8')
        email = info['author_email'].encode('utf-8')
        expected_author = {
            'fullname': b'%s <%s>' % (name, email),
            'name': name,
            'email': email,
        }

        self.assertEqual(expected_author, actual_author)

    def test_no_author(self):
        actual_author = author({})

        self.assertEqual(EMPTY_AUTHOR, actual_author)

    def test_partial_author(self):
        actual_author = author({'author': 'someone'})
        expected_author = {
            'name': b'someone',
            'fullname': b'someone',
            'email': None,
        }

        self.assertEqual(expected_author, actual_author)


class ParseAuthorTest(TestCase):
    def test_author_basic(self):
        data = {
            'author': "i-am-groot",
            'author_email': 'iam@groot.org',
        }
        actual_author = author(data)

        expected_author = {
            'fullname': b'i-am-groot <iam@groot.org>',
            'name': b'i-am-groot',
            'email': b'iam@groot.org',
        }

        self.assertEqual(actual_author, expected_author)

    def test_author_malformed(self):
        data = {
            'author': "['pierre', 'paul', 'jacques']",
            'author_email': None,
        }

        actual_author = author(data)

        expected_author = {
            'fullname': b"['pierre', 'paul', 'jacques']",
            'name': b"['pierre', 'paul', 'jacques']",
            'email': None,
        }

        self.assertEqual(actual_author, expected_author)

    def test_author_malformed_2(self):
        data = {
            'author': '[marie, jeanne]',
            'author_email': '[marie@some, jeanne@thing]',
        }

        actual_author = author(data)

        expected_author = {
            'fullname': b'[marie, jeanne] <[marie@some, jeanne@thing]>',
            'name': b'[marie, jeanne]',
            'email': b'[marie@some, jeanne@thing]',
        }

        self.assertEqual(actual_author, expected_author)

    def test_author_malformed_3(self):
        data = {
            'author': '[marie, jeanne, pierre]',
            'author_email': '[marie@somewhere.org, jeanne@somewhere.org]',
        }

        actual_author = author(data)

        expected_author = {
            'fullname': b'[marie, jeanne, pierre] <[marie@somewhere.org, jeanne@somewhere.org]>',  # noqa
            'name': b'[marie, jeanne, pierre]',
            'email': b'[marie@somewhere.org, jeanne@somewhere.org]',
        }

        self.assertEqual(actual_author, expected_author)

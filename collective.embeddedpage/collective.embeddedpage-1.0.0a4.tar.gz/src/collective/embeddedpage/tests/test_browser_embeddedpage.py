# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from collective.embeddedpage.testing import COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING  # noqa
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest


class EmbeddedPageViewIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(
            'EmbeddedPage',
            id='epage',
            title='Embedded Page'
        )
        self.portal.epage.url = 'https://plone.org'
        self.epage = self.portal.epage

    def test_view_with_get_multi_adapter(self):
        # Get the view
        view = getMultiAdapter((self.epage, self.request), name="view")
        # Put the view into the acquisition chain
        view = view.__of__(self.epage)
        # Call the view
        self.assertTrue(view())

    def test_view_with_restricted_traverse(self):
        view = self.epage.restrictedTraverse('view')
        self.assertTrue(view())

    def test_view_with_unrestricted_traverse(self):
        view = self.epage.unrestrictedTraverse('view')
        self.assertTrue(view())

    # def test_view_html_structure(self):
    #     import lxml
    #     view = getMultiAdapter((self.epage, self.request), name="view")
    #     view = view.__of__(self.epage)
    #     output = lxml.html.fromstring(view())
    #     self.assertEqual(1, len(output.xpath("/html/body/div")))

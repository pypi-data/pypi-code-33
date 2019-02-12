from django.test import TestCase

from .get_site_id import get_site_id, InvalidSiteError


class SiteTests(TestCase):
    def test_all(self):
        self.assertEqual(get_site_id("reviewer"), 1)
        self.assertEqual(get_site_id("gaborone"), 10)
        self.assertEqual(get_site_id("harare"), 20)
        self.assertEqual(get_site_id("lilongwe"), 30)
        self.assertEqual(get_site_id("blantyre"), 40)
        self.assertEqual(get_site_id("capetown"), 50)
        self.assertEqual(get_site_id("kampala"), 60)

    def test_bad(self):
        self.assertRaises(InvalidSiteError, get_site_id, "erik")

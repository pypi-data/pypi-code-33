import unittest
import time

from sbrowser import Browser, be_verbose


class TestBrowser(unittest.TestCase):

    def setUp(self):
        self.browser = Browser()

    def testRequest(self):
        data = self.browser.navigate_to("https://www.uni-hannover.de")
        self.assertTrue(len(data) > 1000)
        self.assertTrue("Leibniz" in str(data))
        self.assertTrue("impressum" in str(data))

    def testTimeout(self):
        before_time = time.perf_counter()
        self.browser.navigate_to("https://www.uni-hannover.de")
        self.browser.navigate_to("https://www.uni-hannover.de")
        after_time = time.perf_counter()
        self.assertTrue((after_time-before_time) > 1.5)

    def testMethod(self):
        with self.assertRaises(AttributeError):
            self.browser.navigate_to("https://www.example.com", method="WHAT")

    def testLastURL(self):
        self.browser.navigate_to("http://hannover.university")
        self.assertEqual(self.browser.lasturl, "https://www.uni-hannover.de/")

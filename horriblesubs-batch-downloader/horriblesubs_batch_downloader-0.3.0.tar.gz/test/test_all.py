import unittest
from unittest.mock import patch

from horriblesubs_batch_downloader import main


class Test12EpisodeShow(unittest.TestCase):

    def test_usage(self):
        scraper, selector, ep_scraper = main('91 days', False)
        assert(True)
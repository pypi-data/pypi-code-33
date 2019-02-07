import unittest

from opensubtitles_downloader import util

""" tv-shows """
filename0 = "The.Simpsons.S01.E04.avi"
filename1 = "The Simpsons-S01-E04.avi"
filename2 = "The_Simpsons_S01_E04.srt"
filename3 = "The.Simpsons.S01xE04.special-edition.avi"

""" not tv-shows """
filename4 = "The.Movie.2016.mkv"
filename5 = "The.Movie.(2016).avi"


class TestTitleRecognise(unittest.TestCase):

    def test_title(self):

        # tv-shows
        self.assertEqual(util.get_title(filename0), "the.simpsons")
        self.assertEqual(util.get_title(filename1), "the.simpsons")
        self.assertEqual(util.get_title(filename2), "the.simpsons")
        self.assertEqual(util.get_title(filename3), "the.simpsons")

        # not tv-shows
        self.assertEqual(util.get_title(filename4), filename4)
        self.assertEqual(util.get_title(filename5), filename5)

    def test_get_season_episode(self):

        # tv-shows
        self.assertEqual(util.get_season_episode(filename0), ('01', '04'))
        self.assertEqual(util.get_season_episode(filename1), ('01', '04'))
        self.assertEqual(util.get_season_episode(filename2), ('01', '04'))
        self.assertEqual(util.get_season_episode(filename3), ('01', '04'))

        # not tv-shows
        self.assertIsNone(util.get_season_episode(filename4))
        self.assertIsNone(util.get_season_episode(filename5))

    def test_same_show_and_episode(self):

        # tv-shows
        self.assertTrue(util.same_show_and_episode(filename0, filename1))
        self.assertTrue(util.same_show_and_episode(filename1, filename2))
        self.assertTrue(util.same_show_and_episode(filename2, filename3))

        # not tv-shows
        self.assertFalse(util.same_show_and_episode(filename0, filename4))
        self.assertFalse(util.same_show_and_episode(filename1, filename5))
        self.assertFalse(util.same_show_and_episode(filename4, filename5))


if __name__ == '__main__':
    unittest.main()

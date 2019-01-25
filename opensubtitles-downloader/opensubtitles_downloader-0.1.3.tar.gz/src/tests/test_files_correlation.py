import unittest

from opensubtitles_downloader import util


class TestFilesCorrelation(unittest.TestCase):

    def test_related_files_perfect_match(self):
        videos = ['The.Simpsons.S01E02.avi', 'American.Dad.S13E01.avi']
        subtitles = ['The.Simpsons.S01E02.srt', 'American.Dad.S13E01.srt']

        result = util.get_related(videos, subtitles)
        expected_result = [(x, y) for x, y in zip(videos, subtitles)]

        self.assertEqual(result, expected_result)

    def test_related_files_single_match(self):
        videos = ['The.Simpsons.S01E02.avi', 'American.Dad.S13E01.avi']
        subtitles = ['The.Simpsons.S01E03.srt', 'American.Dad.S13E01.srt']

        result = util.get_related(videos, subtitles)
        expected_result = [(videos[1], subtitles[1])]

        self.assertEqual(result, expected_result)

    def test_unrelated_files_with_match(self):
        videos = ['The.Simpsons.S01E02.avi', 'American.Dad.S13E01.avi']
        subtitles = ['The.Simpsons.S01E03.srt', 'American.Dad.S13E01.srt']

        result = util.get_unrelated(videos, subtitles)
        expected_result = [videos[0]]

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()

# External dependencies
import pytest

# Local modules
from .context import vigil
from vigil.utils import diff


class TestDiff:
    """
    Class to test Diff.
    """

    old = '<html>\n<h1>Heading 1</h1>\n\n  <p>Text</p>\n</html>'
    updated = '<html>\n<h1>Heading 1</h1>\n<h2>2</h2>\n<p>Change</p>\n</html>'

    def test_strip_html(self):
        """
        Should return string without any html tags.
        """
        test = diff.Diff.strip_html(TestDiff.old)
        sample = '\nHeading 1\n\n  Text\n'
        assert sample == test

    def test_strip_old_content(self):
        """
        Should remove all lines starting with dash.
        """
        test = ['- no', '+ yes']
        sample = '+ yes'

        result = []
        for line in test:
            result.append(diff.Diff.strip_old_content(line))

        assert sample == ''.join(result)

    def test_strip_leading_plus(self):
        """
        Remove all starting pluses.
        """
        test = ['line', '+ new line', '+ another line']
        sample = ['line', 'new line', 'another line']
        result = []
        for line in test:
            result.append(diff.Diff.strip_leading_plus(line))
        assert sample == result

    def test_compare(self):
        """
        Should return a cleaned up diff between two strings.
        """
        test = diff.Diff.compare(TestDiff.old, TestDiff.updated)
        sample = '2\nChange\n'
        assert sample == test

    def test_strip_whitespace(self):
        """
        Remove all whitespace and empty lines.
        """
        test = ['line', '   ', '\n']
        sample = 'line'
        result = []
        for line in test:
            result.append(diff.Diff.strip_whitespace(line))
        assert sample == ''.join(result)

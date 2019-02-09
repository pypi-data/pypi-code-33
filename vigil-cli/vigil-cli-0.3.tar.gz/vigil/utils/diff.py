""" Create a diff of updated sites."""
# Standard modules
import difflib
import html
import re


class Diff:
    """
    Class to get the difference between two strings and clean it up.

    Args:
        old(str): Original string.
        updated(str): Updated string.

    Attributes(str):
        diff(str): Cleaned up representation of the diff.
    """

    def __init__(self, old, updated):
        old = self.strip_html(old)
        updated = self.strip_html(updated)

        raw_diff = difflib.ndiff(old.splitlines(keepends=True),
                                 updated.splitlines(keepends=True),
                                 linejunk=difflib.IS_LINE_JUNK)
        clean_diff = []
        for line in raw_diff:
            line = self.strip_old_content(line)
            line = self.strip_leading_plus(line)
            line = self.strip_whitespace(line)
            clean_diff.append(line)

        self.diff = ''.join(clean_diff)

    @classmethod
    def compare(cls, old, updated):
        """
        Initiates a Diffbuilder instance and returns a cleaned up diff.

        Args:
            old(str): Original string.
            updated(str): Updated string.

        Returns:
            str: Cleaned up representation of a diff.
        """
        return cls(old, updated).diff

    @staticmethod
    def strip_html(webpage):
        """
        Strip html tags.

        Args:
            webpage(str): String to strip HTML tags from.

        Returns:
            str: String without HTML tags.
        """
        tag = False
        quote = False
        stripped = ""

        # First strip all script and css tags
        scripts = re.compile(r'<script.*?/script>', re.DOTALL)
        css = re.compile(r'<style.*?/style>', re.DOTALL)
        webpage = scripts.sub('', webpage)
        webpage = css.sub('', webpage)

        # Then remove other tags procedurally - better than regex at getting
        # faulty html
        for char in webpage:
            if char == '<' and not quote:
                tag = True
            elif char == '>' and not quote:
                tag = False
            elif char in ('"', "'") and tag:
                quote = not quote
            elif not tag:
                stripped = stripped + char

        # Finally, decode html escape sequences
        stripped = html.unescape(stripped)

        return stripped

    @staticmethod
    def strip_old_content(string):
        """
        Strip lines starting with - from given string.

        Args:
            string(str): String to remove lines from.

        Returns:
            str: String without the lines starting with -.
        """
        if string.startswith('+'):
            return string
        return ''

    @staticmethod
    def strip_leading_plus(string):
        """
        Strip the leading plus and whitespace from string

        Args:
            string(str): String to strip leading plus from

        Returns:
            str: String without the leading +.
        """
        if string.startswith('+'):
            return string[2:]
        return string

    @staticmethod
    def strip_whitespace(string):
        """
        Strip leading whitespace and empty lines.

        Args:
            string(str): String to strip whitespace from.

        Returns:
            str: String without leading whitespace.
        """
        if difflib.IS_LINE_JUNK(string):
            return ''
        return string.lstrip()

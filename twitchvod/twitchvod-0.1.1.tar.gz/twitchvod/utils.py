"""twitchvod utils.py"""

import re


def locate_with_default(pattern, input_data, default=None):
    """Locate a pattern in a string if it exists using a regular expression.

    :param pattern: Regular expression to use.
    :type pattern: str.
    :param input_data: Data to run the regex on.
    :type input_data: str.
    :param default: The default value to return if the pattern is not found.

    :returns: The matched data or the default value (None).
    """

    pattern = re.compile(pattern)
    matches = pattern.search(input_data)
    return matches.group(1) if matches else default

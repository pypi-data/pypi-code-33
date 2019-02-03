import re


def has_diacritics(string: str) -> bool:
    """
    Check if the string contains diacritics.

    :param string: String to be checked
    :type string: str
    :return:
    :rtype: bool
    """
    return bool(re.search("[゙゚゛゜]", string))

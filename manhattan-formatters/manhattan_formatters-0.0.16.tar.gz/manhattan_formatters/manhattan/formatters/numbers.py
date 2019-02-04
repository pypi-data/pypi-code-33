import unicodedata
from urllib.parse import parse_qs, urlencode, urlparse

from jinja2.utils import escape as html_escape, urlize
from slugify import slugify as awesome_slugify
from inflection import humanize, titleize

__all__ = [
    'humanize_bytes'
]


def humanize_bytes(number):
    """
    Return a human readable version for the given number of bytes.

    Original source: (Fred Cirera) https://stackoverflow.com/a/1094933/4657956
    """

    for unit in ['','kb','mb','gb','tb','pb','rb','zb']:

        if abs(number) < 1024.0:
            return '%3.1f%s' % (number, unit)

        number /= 1024.0

    return '%.1f%s' % (number, 'yb')
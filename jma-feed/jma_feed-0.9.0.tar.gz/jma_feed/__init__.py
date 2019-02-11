from itertools import chain

from pkg_resources import DistributionNotFound, get_distribution

from jma_feed.feed import AtomFeed, AtomFeedEntry
from jma_feed.report import (
    Report,
    ReportBodyMeteorology,
    ReportBodySeismology,
    ReportBodyVolcanology,
)


try:
    __version__ = get_distribution('jma-feed').version
except DistributionNotFound:
    __version__ = '(local)'


# Minutely Update
FEED_URL_REGULAR_SHORT_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/regular.xml'
FEED_URL_EXTRA_SHORT_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/extra.xml'
FEED_URL_EQVOL_SHORT_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/eqvol.xml'
FEED_URL_OTHER_SHORT_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/other.xml'

# Hourly Update
FEED_URL_REGULAR_LONG_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/regular_l.xml'
FEED_URL_EXTRA_LONG_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/extra_l.xml'
FEED_URL_EQVOL_LONG_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/eqvol_l.xml'
FEED_URL_OTHER_LONG_TERM = 'http://www.data.jma.go.jp/developer/xml/feed/other_l.xml'


def fetch_reports(feed_url):
    """Fetch JMA reports which are listed in feed.

    Args:
        feed_url (str): URL of JMA feed
    """

    feed = AtomFeed(feed_url)
    return [Report(entry.link) for entry in feed.entries]


def fetch_all_reports(long_term=False):
    """Fetch all JMA reports.

    Args:
        long_term (bool): true if use long-term feeds
    """

    if long_term:
        feed_urls = [
            FEED_URL_REGULAR_LONG_TERM,
            FEED_URL_EXTRA_LONG_TERM,
            FEED_URL_EQVOL_LONG_TERM,
            FEED_URL_OTHER_LONG_TERM,
        ]
    else:
        feed_urls = [
            FEED_URL_REGULAR_SHORT_TERM,
            FEED_URL_EXTRA_SHORT_TERM,
            FEED_URL_EQVOL_SHORT_TERM,
            FEED_URL_OTHER_SHORT_TERM,
        ]
    nested_list = [fetch_reports(feed_url) for feed_url in feed_urls]
    return list(chain.from_iterable(nested_list))


def fetch_all_certain_type_reports(long_term=False, report_type=ReportBodyMeteorology):
    return [
        report for report in fetch_all_reports(long_term) if isinstance(report.body, report_type)
    ]


def fetch_all_meteorology_reports(long_term=False):
    """Fetch all JMA meteorology reports.

    Args:
        long_term (bool): true if use long-term feeds
    """

    return fetch_all_certain_type_reports(long_term, ReportBodyMeteorology)


def fetch_all_seismology_reports(long_term=False):
    """Fetch all JMA seismology reports.

    Args:
        long_term (bool): true if use long-term feeds
    """

    return fetch_all_certain_type_reports(long_term, ReportBodySeismology)


def fetch_all_volcanology_reports(long_term=False):
    """Fetch all JMA volcanology reports.

    Args:
        long_term (bool): true if use long-term feeds
    """

    return fetch_all_certain_type_reports(long_term, ReportBodyVolcanology)

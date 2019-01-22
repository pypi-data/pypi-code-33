"""Define the module containing the function used to scrap data from the APD website."""
import asyncio
import datetime
import re
import unicodedata
from urllib.parse import urljoin

import aiohttp
import dateparser
from loguru import logger
from lxml import html

from scrapd.core.constant import Fields

APD_URL = 'http://austintexas.gov/department/news/296'
PAGE_DETAILS_URL = 'http://austintexas.gov/news/'


async def fetch_text(session, url, params=None):
    """
    Fetch the data from a URL as text.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: request URL
    :param dict params: request paramemters, defaults to None
    :return: the data from a URL as text.
    :rtype: str
    """
    if not params:
        params = {}
    async with session.get(url, params=params) as response:
        return await response.text()


async def fetch_news_page(session, page=1):
    """
    Fetch the content of a specific news page from the APD website.

    The page number starts at 1.

    :param aiohttp.ClientSession session: aiohttp session
    :param int page: page number to fetch, defaults to 1
    :return: the page content.
    :rtype: str
    """
    params = {}
    if page > 1:
        params['page'] = page - 1
    return await fetch_text(session, APD_URL, params)


def extract_traffic_fatalities_page_details_link(news_page):
    """
    Extract the fatality detail page links from the news page.

    :param str news_page: html content of the new pages
    :return: a list of links.
    :rtype: list or `None`
    """
    PATTERN = r'<a href="(/news/traffic-fatality-\d{1,3}-\d)">(Traffic Fatality #(\d{1,3}))</a>'
    regex = re.compile(PATTERN)
    matches = regex.findall(news_page, re.MULTILINE)
    return matches


def generate_detail_page_urls(titles):
    """
    Generate the full URLs of the fatality detail pages.

    :param list titles: a list of partial link
    :return: a list of full links to the fatality detail pages.
    :rtype: list
    """
    return [urljoin(PAGE_DETAILS_URL, title[0]) for title in titles]


def has_next(news_page):
    """
    Return `True` if there is another news page available.

    :param str news_page: the news page to parse
    :return: `True` if there is another news page available, `False` otherwise.
    :rtype: bool
    """
    if not news_page:
        return False

    NEXT_XPATH = '/html/body/div[3]/div[2]/div[2]/div[2]/div/div/div/div/div[2]/div[3]/div/div/div/div[3]/ul/li[3]/a'
    root = html.fromstring(news_page)
    elements = root.xpath(NEXT_XPATH)
    return bool(elements)


def parse_twitter_title(twitter_title):
    """
    Parse the Twitter tittle metadata.

    :param str twitter_title: Twitter tittle embedded in the fatality details page
    :return: A dictionary containing the 'Fatal crashes this year' field.
    :rtype: dict
    """
    d = {}
    if not twitter_title:
        return d

    # Extract the fatality number from the title.
    match = re.search(r'\d{1,3}', twitter_title)
    if match:
        d[Fields.CRASHES] = match.group()

    return d


def parse_twitter_description(twitter_description):
    """
    Parse the Twitter description metadata.

    The Twitter description contains all the information that we need, and even though it is still unstructured data,
    it is easier to parse than the data from the detail page.

    :param str twitter_description: Twitter description embedded in the fatality details page
    :return: A dictionary containing the details information about the fatality.
    :rtype: dict
    """
    d = {}
    if not twitter_description:
        return d

    # Split the description to be able to parse it.
    current_field = None
    description_words = twitter_description.split()
    for word in description_words:
        # A word ending with a colon (':') is considered a field.
        if word.endswith(':'):
            current_field = word.replace(':', '')
            continue
        d.setdefault(current_field, []).append(word)

    # Parse the Deceased field.
    if d.get(Fields.DECEASED):
        try:
            d.update(parse_deaceased_field(d.get(Fields.DECEASED)))
        except ValueError as e:
            logger.trace(e)
    else:
        logger.trace('No decease information to parse in Twitter description.')

    # Compute the victim's age.
    if d.get(Fields.DATE) and d.get(Fields.DOB):
        d[Fields.AGE] = compute_age(' '.join(d.get(Fields.DATE)), d.get(Fields.DOB))

    return sanitize_fatality_entity(d)


def compute_age(date, dob):
    """
    Compute a victim's age.

    :param str date: crash date
    :param str dob: date of birth
    :return: the victim's age.
    :rtype: int
    """
    DAYS_IN_YEAR = 365
    dob_ = dateparser.parse(dob)

    # In case the date of birth only contains 2 digits, we have to determine whether it should be
    # 19xx or 20xx.
    now = datetime.datetime.now()
    if dob_.year > now.year:
        dob_ = datetime.datetime(dob_.year - 100, dob_.month, dob_.day)

    # Compute the age.
    return (dateparser.parse(date) - dob_).days // DAYS_IN_YEAR


def sanitize_fatality_entity(d):
    """
    Clean up a fatality entity.

    Ensures that the values are all strings and removes the 'Deceased' field which does not contain
    relevant information anymore.

    :param dict d: the fatality to sanatize
    :return: A dictionary containing the details information about the fatality with sanitized entries.
    :rtype: dict
    """
    # All values must be strings.
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = ' '.join(v)

    # The 'Deceased' field is unnecessary.
    if d.get('Deceased'):
        del d['Deceased']

    return d


def parse_deaceased_field(deceased_field):
    """
    Parse the deceased field.

    At this point the deceased field, if it exists, is garbage as it contains First Name, Last Name, Ethnicity,
    Gender, D.O.B. and Notes. We need to explode this data into the appropriate fields.

    :param list deceased_field: a list where each item is a word from the deceased field
    :return: a dictionary representing a deceased field.
    :rtype: dict
    """
    dob_index = -1
    dob_tokens = [Fields.DOB, '(D.O.B', '(D.O.B.', '(D.O.B:', '(DOB', '(DOB:', 'D.O.B.', 'DOB:']
    while dob_index < 0 and dob_tokens:
        dob_token = dob_tokens.pop()
        try:
            dob_index = deceased_field.index(dob_token)
        except ValueError:
            pass
        else:
            break

    if dob_index < 0:
        raise ValueError(f'Cannot parse {Fields.DECEASED}: {deceased_field}')

    d = {}
    d[Fields.DOB] = deceased_field[dob_index + 1]
    notes = deceased_field[dob_index + 2:]
    if notes:
        d[Fields.NOTES] = ' '.join(notes)

    # `fleg` stands for First, Last, Ethnicity, Gender. It represents the info stored before the DOB.
    fleg = deceased_field[:dob_index]

    # Try to pop out the results one by one. If pop fails, it means there is nothing left to retrieve,
    # For example, there is no first name and last name.
    try:
        d[Fields.GENDER] = fleg.pop().replace(',', '')
        d[Fields.ETHNICITY] = fleg.pop().replace(',', '')
        d[Fields.LAST_NAME] = fleg.pop().replace(',', '')
        d[Fields.FIRST_NAME] = fleg.pop().replace(',', '')
    except IndexError:
        pass

    return d


def parse_page_content(detail_page):
    """
    Parse the detail page to extract fatality information.

    :param str news_page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    d = {}
    searches = [
        (Fields.CASE, re.compile(r'Case:.*\s([0-9\-]+)<')),
        (Fields.CRASHES, re.compile(r'Traffic Fatality #(\d{1,3})')),
        (Fields.DATE, re.compile(r'>Date:.*\s{2,}([^<]*)</')),
        (Fields.DECEASED, re.compile(r'>Deceased:.*\s{2,}([^<]*\d)\)?<')),
        (Fields.LOCATION, re.compile(r'>Location:.*>\s{2,}([^<]+)')),
        (Fields.TIME, re.compile(r'>Time:.*>\s{2,}([^<]+)')),
    ]
    normalized_detail_page = unicodedata.normalize("NFKD", detail_page)
    for search in searches:
        match = re.search(search[1], normalized_detail_page)
        if match:
            d[search[0]] = match.groups()[0]

    # Parse the Deceased field.
    if d.get(Fields.DECEASED):
        try:
            d.update(parse_deaceased_field(d.get(Fields.DECEASED).split()))
        except ValueError as e:
            logger.trace(e)
    else:
        logger.trace('No decease information to parse in fatality page.')

    # Compute the victim's age.
    if d.get(Fields.DATE) and d.get(Fields.DOB):
        d[Fields.AGE] = compute_age(d.get(Fields.DATE), d.get(Fields.DOB))

    return sanitize_fatality_entity(d)


def parse_twitter_fields(page):
    """
    Parse the Twitter fields on a detail page.

    :param str page: the content of the fatality page
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    TWITTER_TITLE_XPATH = '/html/head/meta[@name="twitter:title"]'
    TWITTER_DESCRIPTION_XPATH = '/html/head/meta[@name="twitter:description"]'

    # Collect the elements.
    html_ = html.fromstring(page)
    elements = html_.xpath(TWITTER_TITLE_XPATH)
    twitter_title = elements[0].get('content') if elements else ''
    elements = html_.xpath(TWITTER_DESCRIPTION_XPATH)
    twitter_description = elements[0].get('content') if elements else ''

    # Parse the elements.
    title_d = parse_twitter_title(twitter_title)
    desc_d = parse_twitter_description(twitter_description)
    d = {**title_d, **desc_d}
    return d


def parse_page(page):
    """
    Parse the page using all parsing methods available.

    :param str  page: the content of the fatality page
    """
    # Parse the page.
    twitter_d = parse_twitter_fields(page)
    page_d = parse_page_content(page)

    # Merge the results, from right to left.
    # (i.e. the rightmost object will overiide the object just before it, etc.)
    d = {**page_d, **twitter_d}
    return d


async def fetch_and_parse(session, url):
    """
    Parse a fatality page from a URL.

    :param aiohttp.ClientSession session: aiohttp session
    :param str url: detail page URL
    :return: a dictionary representing a fatality.
    :rtype: dict
    """
    # Retrieve the page.
    page = await fetch_text(session, url)

    # Parse it.
    d = parse_page(page)

    # Add the link.
    d[Fields.LINK] = url

    # Return the result.
    return d


def is_in_range(date, from_=None, to=None):
    """
    Check whether a date is comprised between 2 others.

    :param str date: date to vheck
    :param str from_: start date, defaults to None
    :param str to: end date, defaults to None
    :return: `True` if the date is between `from_` and `to`
    :rtype: bool
    """

    current_date = dateparser.parse(date)
    from_date = dateparser.parse(from_, settings={'PREFER_DAY_OF_MONTH': 'first'}) if from_ else datetime.datetime.min
    to_date = dateparser.parse(to, settings={'PREFER_DAY_OF_MONTH': 'last'}) if to else datetime.datetime.max

    return from_date <= current_date <= to_date


async def async_retrieve(pages=-1, from_=None, to=None):
    """Retrieve fatality data."""
    res = []
    page = 1
    has_entries = False
    async with aiohttp.ClientSession() as session:
        while True:
            # Fetch the news page.
            logger.info(f'Fetching page {page}...')
            news_page = await fetch_news_page(session, page)

            # Looks for traffic fatality links.
            page_details_links = extract_traffic_fatalities_page_details_link(news_page)

            # Generate the full URL for the links.
            links = generate_detail_page_urls(page_details_links)
            logger.debug(f'{len(links)} fatality page(s) to process.')

            # Fetch and parse each link.
            tasks = [fetch_and_parse(session, link) for link in links]
            page_res = await asyncio.gather(*tasks)

            # If the page contains fatalities, ensure all of them happened within the specified time range.
            if page_res:
                entries_in_time_range = [entry for entry in page_res if is_in_range(entry[Fields.DATE], from_, to)]
                if not has_entries:
                    has_entries = not has_entries and bool(entries_in_time_range)
                logger.debug(f'{len(entries_in_time_range)} fatality page(s) is/are within the specified time range.')

                # If there are none in range, we do not need to search further, and we can discard the results.
                if has_entries and not entries_in_time_range:
                    logger.debug(f'There are no data within the specified time range on page {page}.')
                    break

                # Otherwise store the results.
                res += entries_in_time_range

            # Stop if there is no further pages.
            if not has_next(news_page):
                break

            if page >= pages > 0:
                break

            page += 1

    return res

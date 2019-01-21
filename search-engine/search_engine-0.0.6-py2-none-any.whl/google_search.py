# _*_ coding: utf-8 _*_

import os
import random
import sys
import time
import math
import traceback

import six
import requests

import logging

from six.moves.urllib.parse import quote
from six.moves.urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
    is_bs4 = True
except ImportError:
    from BeautifulSoup import BeautifulSoup
    is_bs4 = False

# URL templates to make Google searches.
url_home = "http://%(gip)s/"
url_search = "http://%(gip)s/search?hl=%(lang)s&q=%(query)s&" \
             "btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
url_next_page = "http://%(gip)s/search?hl=%(lang)s&q=%(query)s&" \
                "start=%(start)d&tbs=%(tbs)s&safe=%(safe)s&tbm=%(tpe)s"
url_search_num = "http://%(gip)s/search?hl=%(lang)s&q=%(query)s&" \
                 "num=%(num)d&btnG=Google+Search&tbs=%(tbs)s&safe=%(safe)s&" \
                 "tbm=%(tpe)s"
url_next_page_num = "http://%(gip)s/search?hl=%(lang)s&" \
                    "q=%(query)s&num=%(num)d&start=%(start)d&tbs=%(tbs)s&" \
                    "safe=%(safe)s&tbm=%(tpe)s"

dir_path = os.path.dirname(os.path.realpath(__file__))

# Default user agent, unless instructed by the user to change it.
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

# Request the given URL and return the response page, using the cookie jar.
def get_page(url):
    text = ""
    try:
        resp = requests.get(url, headers={
            "User-Agent": USER_AGENT,
        }, timeout=10)
        text = resp.text
    except:
        logging.info(traceback.format_exc())
    return text

# Filter links found in the Google result pages HTML code.
# Returns None if the link doesn't yield a valid result.
def filter_result(link):
    try:

        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse.urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        # Decode hidden URLs.
        if link.startswith('/url?'):
            link = urlparse.parse_qs(o.query)['q'][0]

            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse.urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None

def nextip():
    ips = open(os.path.join(dir_path, "google_ip.txt")  , "r+").readlines()
    ips = [ip.strip() for ip in ips]
    i = 0
    while i < len(ips):
        yield ips[i]
        i += 1
nips = nextip()
global_gip = six.next(nips)

def update_gip():
    global global_gip
    try:
        global_gip = six.next(nips)
    except StopIteration:
        raise IpDrainException("ip drained")

class IpDrainException(Exception):
    pass 

# Returns a generator that yields URLs.
def google(query, tld='com', lang='zh-cn', tbs='0', safe='off', num=10, start=0,
           stop=None, domains=None, pause=2.0, only_standard=False,
           extra_params={}, tpe='', user_agent=None):
    """
    Search the given query string using Google.

    @type  query: str
    @param query: Query string. Must NOT be url-encoded.

    @type  tld: str
    @param tld: Top level domain.

    @type  lang: str
    @param lang: Language.

    @type  tbs: str
    @param tbs: Time limits (i.e "qdr:h" => last hour,
        "qdr:d" => last 24 hours, "qdr:m" => last month).

    @type  safe: str
    @param safe: Safe search.

    @type  num: int
    @param num: Number of results per page.

    @type  start: int
    @param start: First result to retrieve.

    @type  stop: int
    @param stop: Last result to retrieve.
            Use C{None} to keep searching forever.

    @type  domains: list
    @param domains: A list of web domains to constrain the search.

    @type  pause: float
    @param pause: Lapse to wait between HTTP requests.
        A lapse too long will make the search slow, but a lapse too short may
        cause Google to block your IP. Your mileage may vary!

    @type  only_standard: bool
    @param only_standard: If C{True}, only returns the standard results from
        each page. If C{False}, it returns every possible link from each page,
        except for those that point back to Google itself. Defaults to C{False}
        for backwards compatibility with older versions of this module.

    @type  extra_params: dict
    @param extra_params: A dictionary of extra HTTP GET parameters, which must
        be URL encoded. For example if you don't want google to filter similar
        results you can set the extra_params to {'filter': '0'} which will
        append '&filter=0' to every query.

    @type  tpe: str
    @param tpe: Search type (images, videos, news, shopping, books, apps)
            Use the following values {videos: 'vid', images: 'isch',
                                      news: 'nws', shopping: 'shop',
                                      books: 'bks', applications: 'app'}

    @type  user_agent: str
    @param user_agent: User agent for the HTTP requests. Use C{None} for the
        default.

    @rtype:  generator
    @return: Generator (iterator) that yields found URLs. If the C{stop}
        parameter is C{None} the iterator will loop forever.
    """
    global global_gip, nips
    if global_gip == None:
        update_gip()

    gip = global_gip

    # Set of hashes for the results found.
    # This is used to avoid repeated results.
    hashes = set()

    # Count the number of links yielded
    count = 0

    # Prepare domain list if it exists.
    if domains:
        query = query + ' ' + ' OR '.join(
                                'site:' + domain for domain in domains)

    # Prepare the search string.
    query = quote(query)

    # Check extra_params for overlapping
    for builtin_param in ('hl', 'q', 'btnG', 'tbs', 'safe', 'tbm'):
        if builtin_param in extra_params.keys():
            raise ValueError(
                'GET parameter "%s" is overlapping with \
                the built-in GET parameter',
                builtin_param
            )

    blankCount = 0
    # Loop until we reach the maximum result, if any (otherwise, loop forever).
    while not stop or start < stop:

        # Prepare the URL of the first request.
        if start:
            if num == 10:
                url = url_next_page % vars()
            else:
                url = url_next_page_num % vars()
        else:
            if num == 10:
                url = url_search % vars()
            else:
                url = url_search_num % vars()


        try:  # Is it python<3?
            iter_extra_params = extra_params.iteritems()
        except AttributeError:  # Or python>3?
            iter_extra_params = extra_params.items()
        # Append extra GET_parameters to URL
        for k, v in iter_extra_params:
            url += url + ('&%s=%s' % (k, v))

        # Sleep between requests.
        time.sleep(pause)

        # Request the Google Search results page.
        logging.info("search: %s" % url)
        html = get_page(url)

        if html == "" or html is None:
            logging.info("change google ip")
            update_gip()
            gip = global_gip
            logging.info("%s %s" % (global_gip, gip))
            continue

        # Parse the response and process every anchored URL.
        if is_bs4:
            soup = BeautifulSoup(html, 'html.parser')
        else:
            soup = BeautifulSoup(html)
        anchors = soup.find(id='search').findAll('a')
        
        #print(soup.find("title").contents[0])
        if soup.find("title").contents[0].find("403") > -1:
            logging.info("google forbidden, update")
            update_gip()
            gip = global_gip
            logging.info("%s %s" % (global_gip, gip))
            continue

        logging.info("archors: %d" % len(anchors))

        if len(anchors) == 0:
            blankCount += 1
            if blankCount >= 3:
                break

        for a in anchors:

            # Leave only the "standard" results if requested.
            # Otherwise grab all possible links.
            if only_standard and (
                    not a.parent or a.parent.name.lower() != "h3"):
                continue

            # Get the URL from the anchor tag.
            try:
                link = a['href']
            except KeyError:
                continue

            # Filter invalid links and links pointing to Google itself.
            link = filter_result(link)
            if not link:
                continue

            logging.info("link: %s" % link)

            # Discard repeated results.
            h = hash(link)
            if h in hashes:
                continue
            hashes.add(h)

            # Yield the result.
            yield link

            count += 1
            if stop and count >= stop:
                return

        # End if there are no more results.
        if not soup.find(id='nav'):
            break

        # Prepare the URL for the next request.
        start += num
        if num == 10:
            url = url_next_page % vars()
        else:
            url = url_next_page_num % vars()

def google_verified(keyword):
    for link in google(keyword):
        try:
            r = requests.get(link)
            if r.text.find(keyword) > -1:
                yield link
        except:
            logging.info(traceback.format_exc())

if __name__ == "__main__":
    for link in google_verified("myvyang"):
        print(link)

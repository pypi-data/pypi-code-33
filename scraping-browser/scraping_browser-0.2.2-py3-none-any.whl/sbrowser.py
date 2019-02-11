#!/usr/bin/env python3
"""Scraping Browser to emulate a somehow working browser."""


import warnings
from time import sleep, perf_counter
from random import choice, random
from urllib.parse import urlsplit
import logging

import requests

logging.basicConfig()
LOG = logging.getLogger("sbrowser")

DESKTOP_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko"
    ") Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Geck"
    "o) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
    " Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHT"
    "ML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Geck"
    "o) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML"
    ", like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML"
    ", like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko"
    ") Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like "
    "Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
]

def be_verbose():
    """Set logging level to high."""
    LOG.setLevel(logging.DEBUG)

def url_to_tld_hostname(site):
    """Return hostname and TDL from URL."""
    # finding out the hostname
    hostname = urlsplit(site).hostname.lower()
    tld = hostname[hostname.rfind("."):]
    hostname = hostname[: hostname.rfind(".")]
    if "." in hostname:
        hostname = hostname[hostname.rfind(".") + 1:]
    return hostname + tld


def goto(site, payload=None, method="GET"):
    """
    Simple and fast goto.

    This function allows the user to navigate to a web page.
    """
    warnings.warn("Call to deprecated function goto. " +
                  "Please use navigate_to() from class Browser instead.",
                  category=DeprecationWarning)
    sbrowser = Browser.get_instance()
    sbrowser.navigate_to(site, payload, method)


class Browser:
    """Class to emulate a browser."""
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not Browser.__instance:
            Browser.__instance = Browser()
        return Browser.__instance

    def __init__(self):
        """Initialize with sane values."""
        self.idletime = 1500
        self._sites = {}
        self._cookies = {}
        self.lasturl = "about:blank"
        self._verbosity = 2

    def clear_cookies(self, site=None):
        """Remove all cookies or for a specific site."""
        if not site:
            self._cookies = {}
        else:
            hostname = url_to_tld_hostname(site)
            if hostname in self._cookies.keys():
                self._cookies[site] = {}

    def _sleep_if_necessary(self, hostname):
        """Reduce the accessess to a website by sleeping if previously visited"""
        curr_time = perf_counter()
        if hostname in self._sites.keys():
            last_time = self._sites[hostname]
            if curr_time - last_time < self.idletime:
                sleeptime = (
                    self.idletime
                    - (curr_time - last_time)
                    + self.idletime * random()
                ) / 1000
                LOG.debug("[Browser] Request to frequent, sleeping {0:.1f} "
                          "seconds before going there.".format(sleeptime))
                sleep(sleeptime)
        self._sites[hostname] = perf_counter()

    def navigate_to(self, site, payload=None, method="GET"):
        """Method to navigate the browser to a new site."""
        LOG.debug("[Browser] Going to site %s", site)
        hostname = url_to_tld_hostname(site)

        self._sleep_if_necessary(hostname)

        headers = {
            "User-Agent": choice(DESKTOP_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/webp,*/*;q=0.8",
        }

        cookie = {}
        if hostname in self._cookies.keys():
            cookie = self._cookies[hostname]

        if method == "GET":
            req = requests.get(
                site,
                headers=headers,
                data=payload,
                cookies=cookie,
                timeout=(6.05, 60),
            )
        elif method == "POST":
            req = requests.post(
                site,
                headers=headers,
                data=payload,
                cookies=cookie,
                timeout=(6.05, 60),
            )
        elif method == "PUT":
            req = requests.post(
                site,
                headers=headers,
                data=payload,
                cookies=cookie,
                timeout=(6.05, 60),
            )
        else:
            raise AttributeError('No such method"{}"'.format(method))
        self.lasturl = req.url
        cookie = req.cookies
        if cookie:
            self._cookies[hostname] = cookie
        self._sites[hostname] = perf_counter()
        return req.content

#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from acm."""

# Common libraries
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Self written libraries
import sbrowser

from .landing_page import LandingPage


class Acm(LandingPage):
    """
    Parser for acm.

    https://dl.acm.org
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from acm.

        @return BibTex from soup
        """
        for links in self.soup.find_all('a'):
            if "BibTeX" in links:
                nexturl = links.get("href")
                nexturl = nexturl[nexturl.find("exportformats"):]
                nexturl = nexturl[:nexturl.find("'")]
                nexturl = urljoin(self.link, nexturl)
                page = sbrowser.goto(nexturl)
                soup = BeautifulSoup(page, 'html.parser')
                content = soup.find("pre")
                return content.string
        return None

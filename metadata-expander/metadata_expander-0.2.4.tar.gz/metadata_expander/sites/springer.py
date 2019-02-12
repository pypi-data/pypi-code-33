#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from springer."""

# Common libraries
from urllib.parse import urljoin

# Self written libraries
import sbrowser
from metadata_expander.custom_exceptions import IsABookException

from .landing_page import LandingPage


class Springer(LandingPage):
    """
    Parser for springer.

    https://link.springer.com/
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from springer.

        @return BibTex from soup
        """
        if "/book/" in self.link:
            raise IsABookException
        for link in self.soup.find_all('a'):
            if "bibtex" in link.get("href"):
                nexturl = urljoin(self.link, link.get("href"))
                page = sbrowser.goto(nexturl)
                return page.decode()
        return None

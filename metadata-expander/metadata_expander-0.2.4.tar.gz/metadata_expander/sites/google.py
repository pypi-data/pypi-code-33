#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from google scholar."""

from bs4 import BeautifulSoup

import sbrowser
from metadata_expander.custom_exceptions import DocumentNotFound

from .landing_page import LandingPage


class Google(LandingPage):
    """
    Parser for google scholar.

    https://scholar.google.com
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from google scholar.

        Requests link again with new cookie for easier BibTeX access
        May not return any result, searches document by e.g. title
        No guarantee that the document exists. (Opposed to a doi look up)
        @return BibTex from link
        """
        cookie = "GSP=CF=4"
        page = sbrowser.goto(self.link, cookie)
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.find_all("a", class_="gs_nta gs_nph"):
            if ".bib" in link.get("href"):
                nexturl = link.get("href")
                page = sbrowser.goto(nexturl)
                bib = page.read().decode()
                return bib
        raise DocumentNotFound

#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from dblp uni-trier."""

from bs4 import BeautifulSoup
import sbrowser

# Self written libraries
from metadata_expander.custom_exceptions import DocumentNotFound

from .landing_page import LandingPage


class Unitrier(LandingPage):
    """
    Parser for dblp from university trier.

    https://dblp.uni-trier.de/
    """

    def get_link_to_bib(self):
        """
        Get link to site with BibTeX from search result.

        @return link to site with BibTex
        """
        for ulist in self.soup.find_all("ul", {"class": "publ-list"}):
            for link in ulist.find_all("a"):
                if "bibtex" in link.get("href"):
                    return link.get("href")
        raise DocumentNotFound

    def get_bibtex(self):
        """
        Retrieve BibTex from unitrier.

        May not return any result, searches document by e.g. title
        No guarantee that the document exists. (Opposed to a doi look up)
        @return BibTex from link
        """
        link = self.get_link_to_bib()
        page = sbrowser.goto(link)
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.find_all("a"):
            if link.get("href").endswith(".bib"):
                nexturl = link.get("href")
                page = sbrowser.goto(nexturl)
                return page.decode()
        return None

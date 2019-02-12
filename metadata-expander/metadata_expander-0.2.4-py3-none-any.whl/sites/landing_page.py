#!/usr/bin/env python3
# pylint: disable=assignment-from-none,no-self-use
"""Generic Class for scraping."""

import bibtexparser
from metadata_expander.custom_exceptions import IsABookException


class LandingPage():
    """
    Return the metadata for any available site.

    Parent class for selecting get_bibtex or get_dict
    Subclass must overwrite one of them!
    """

    def __init__(self):
        """Self init."""
        self.link = ""
        self.soup = None

    def get_bibtex(self): # noqa: D401
        """Dummy for BibTeX."""
        return None

    def get_dict(self): # noqa: D401
        """Dummy for dictionary."""
        return None

    def get_content(self, link: str, soup):
        """
        Return metadata.

        Select the right function, get_bibtex or get_dict
        @param link to site
        @param soup parsed site
        @return metadata from link or soup
        """
        self.link = link
        self.soup = soup
        info = None
        try:
            bibtex = self.get_bibtex()
            if bibtex is not None:
                info = bibtexparser.loads(bibtex).entries
                if info:
                    info = info[0]
            else:
                info = self.get_dict()
        except IsABookException:
            print("The DOI you specified is a book. Please refer to a paper!")
        else:
            return info

#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from elsevier."""

# Common libraries
import sbrowser

# Self written libraries
from .landing_page import LandingPage


class Elsevier(LandingPage):
    """
    Parser for elsevier.

    https://www.elsevier.de
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from elsevier.

        @return BibTex from soup
        """
        for link in self.soup.find_all('input'):
            if "id" in link.get("id"):
                url = "https://www.sciencedirect.com/sdfe/arp/cite?" + \
                      "format=text/x-bibtex&withabstract=true&pii=" + \
                      link.get("value")
                return sbrowser.goto(url)
        return None

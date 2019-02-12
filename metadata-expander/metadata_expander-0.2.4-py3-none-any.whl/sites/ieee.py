#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from ieee."""

# Common libraries
import sbrowser

# Self written libraries
from .landing_page import LandingPage


class Ieee(LandingPage):
    """
    Parser for ieee.

    https://ieeexplore.ieee.org/Xplore/home.jsp
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from ieee.

        @return BibTex from link
        """
        record_id = self.link
        if record_id[-1] == "/":
            record_id = record_id[:-1]
        record_id = record_id[record_id.rfind("/") + 1:]
        url = "https://ieeexplore.ieee.org/xpl/downloadCitations"
        data = {
            "citations-format": "citation-only",
            "download-format": "download-bibtex",
            "recordIds": record_id,
        }
        bib = sbrowser.goto(url, payload=data, method="POST")
        bib = bib.decode().replace("<br>", "")
        return bib

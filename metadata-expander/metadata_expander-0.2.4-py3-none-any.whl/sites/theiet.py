#!/usr/bin/env python3
"""Class for retrieving metadata as BibTeX from theiet."""

# Common libraries

# Self written libraries
import sbrowser

from .landing_page import LandingPage


class Theiet(LandingPage):
    """
    Parser for theiet.

    http://digital-library.theiet.org/
    """

    def get_bibtex(self):
        """
        Retrieve BibTex from theiet.

        @return BibTex from soup
        """
        nexturl = self.link + "/cite/bibtex"
        content = sbrowser.goto(nexturl)
        return content.decode()

#!/usr/bin/env python3
# pylint: disable=no-self-use,pointless-string-statement
"""Example Class for retrieving metadata as BibTeX or dict from a site."""

# Self written libraries
from .landing_page import LandingPage
""" Please use the browser class if possible and not urllib!"""


class Example(LandingPage):
    """
    Class name must be the filename.

    Filename must be lowercase, the Class name must begin with a upper case
    and the rest lower case.
    """

    """Only one function shall be implemented the superclass will select the
       right one and execute it."""

    """Some publisher provide Bibtex for their papers. For them this function
       should be preferred"""
    def get_bibtex(self):
        """Replace this with a working docstring."""
        return None

    """ if there is no way of simply getting a BibTeX file, one can also
        create a python dictionary. It should follow the Dublin Core standard
        for the field names, which can sometimes be a bit tricky."""
    def get_dict(self):
        """Replace this with a working docstring."""
        return None

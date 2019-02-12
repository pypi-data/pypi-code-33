#!/usr/bin/env python3
"""Class for retrieving metadata as dict from iospress."""

# Common libraries
from bs4 import NavigableString

# Self written libraries
from .landing_page import LandingPage


class Iospress(LandingPage):
    """
    Parser for iospress.

    https://content.iospress.com/
    """

    def get_dict(self):
        """
        Retrieve dictionary from iospress.

        @return dictionary from soup
        """
        info = {}

        for headline in self.soup.find_all("h1"):
            title = headline.get("data-p13n-title")
            if title is not None:
                info['title'] = title
                break

        for paragraph in self.soup.find_all("p", class_="metadata-entry"):
            key = paragraph.contents[0].text[:-2]
            if isinstance(paragraph.contents[1], NavigableString):
                value = paragraph.contents[1]
            else:
                value = paragraph.contents[1].text

            info[key] = value

        return info

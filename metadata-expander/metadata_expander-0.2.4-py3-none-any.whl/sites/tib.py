#!/usr/bin/env python3
"""Class for retrieving metadata as dict from theiet."""

from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup

# Self written libraries
import sbrowser

from .landing_page import LandingPage


class Tib(LandingPage):
    """
    Parser for tib.

    http://digital-library.theiet.org/
    Used as backup if the original site fails
    """

    def get_dict(self):
        """
        Retrieve dictionary from tib.

        @return dictionary from soup
        """
        dictionary = {}
        ulist = self.soup.select("ul[class=information]")[0]
        for list_item in ulist.select("li"):
            name, cont = get_field_content(list_item)
            dictionary[name] = cont
        return dictionary


def get_url_from_doi(doi):
    """
    Get link to document from doi.

    @param doi of document
    @return link for document
    """
    doi = quote(doi, safe="")
    link = "https://www.tib.eu/en/search/? " + \
           "tx_tibsearch_search%5Bquery%5D={}".format(doi)
    page = sbrowser.goto(link)
    soup = BeautifulSoup(page, 'html.parser')
    hits = soup.select("div[id=hitlist]")
    if not hits:
        print("[tib] Could not find document using doi: " + doi)
        return None
    div = hits[0]
    list_item = div.select("li")
    link2 = None
    if len(list_item) == 1:
        list_item = list_item[0]
        for link3 in list_item.select("a"):
            href = link3["href"]
            link2 = urljoin(link, href)
    return link2


def get_field_content(list_item):
    """
    Get metadata from html list object.

    @param li html list object parsed with soup
    @return key and value for metadata
    """
    field = list_item.select("div[class=field]")[0].text.strip()[:-1]
    description = list_item.select("div[class=description]")[0]
    links = description.find_all("a")
    content = []
    if links:
        for child in links:
            content.append(child.text.strip())
    else:
        content.append(description.text.strip())
    return field, content

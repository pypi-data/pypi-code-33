#!/usr/bin/env python3
"""
Contains various methods to retrieve metadata.

Available is a search with: doi, metadata, search string, link
"""
from importlib import import_module
from urllib.error import URLError
from urllib.parse import quote, urljoin, urlsplit

# Common libraries
from bs4 import BeautifulSoup

# Self written libraries
from sbrowser import Browser
from .custom_exceptions import DocumentNotFound

DBLP = "https://dblp.uni-trier.de/search?q={}"
GOOGLE_SCHOLAR = "https://scholar.google.de/scholar?" + \
                 "hl=de&as_sdt=0%2C5&q={}&btnG="


def search_link(link: str, doi: str = None):
    """
    Search for metadata using a link.

    Request a page from the input link and load the
    corresponding module to parse the page.
    If there is no module matching module, tib is used as default.
    @param link to a specific document or a search result
    @return found metadata
    """
    sbrowser = Browser.get_instance()
    soup = BeautifulSoup(sbrowser.navigate_to(link), 'html.parser')
    link = sbrowser.lasturl

    # finding out the hostname part of the landing page
    hostname = urlsplit(link).hostname.lower().replace("-", "")
    hostname = hostname[:hostname.rfind(".")]
    if "." in hostname:
        hostname = hostname[hostname.rfind(".") + 1:]

    module_name = hostname[0].upper() + hostname[1:]

    # dynamically loading the module for the new hostname
    print("trying to load module " + hostname)
    data = ""
    module = None
    try:
        module = getattr(
            import_module("{}.{}".format("metadata_expander.sites", hostname)),
            module_name,
        )()
    except ImportError:
        print("Could not find a module for " + link)
        if not doi:
            return None

        print("Trying to search via tib.de")
        hostname = "tib"
        module = getattr(
            import_module("{}.{}".format("metadata_expander.sites", hostname)),
            module_name,
        )()
        link = module.get_url_from_doi(doi)
        if not link:
            return None
        page = sbrowser.goto(link)
        soup = BeautifulSoup(page, 'html.parser')

    data = module.get_content(link, soup)

    return data


def search_doi(doi: str):
    """
    Search using a doi.

    @param doi
    @return found metadata
    """
    doi = doi.split(":", 1)[-1]
    link = urljoin("https://dx.doi.org/", doi)
    return search_link(link, doi)


def search_string(search_term: str):
    """
    Search using a string of metadata.

    @param search_term string of metadata
    @return found metadata
    """
    search_term = quote(search_term, safe="")
    # search on dblp
    try:
        print("Searching on dblp")
        link = DBLP.format(search_term)
        return search_link(link)
    except DocumentNotFound:
        pass

    # search on google scholar
    try:
        print("No document found on DBLP, trying google scholar")
        link = GOOGLE_SCHOLAR.format(search_term)
        return search_link(link)
    except DocumentNotFound:
        print("No document found on google scholar")
        raise


def search_meta(meta: dict):
    """
    Search by using a dictionary of metadata.

    If a doi is in the dictionary, the doi is used
    in a seperate search, because it will find the correct document
    or none, while a search with the title might find a wrong document.
    @param meta dictionary of metadata
    @return found metadata
    """
    result = {}
    doi = None

    # do not use doi for a search query
    if "identifier" in meta:
        doi = meta.pop("identifier")

    values = " ".join(value for value in meta.values())
    try:
        result.update(search_string(values))
    except DocumentNotFound:
        pass

    # If update hits duplicate keys, the new ones are used.
    # Since doi is unique (opposed to the earlier search query),
    # this overwrite is wanted
    if doi:
        try:
            result.update(search_doi(doi))
        except URLError:
            pass

    return result

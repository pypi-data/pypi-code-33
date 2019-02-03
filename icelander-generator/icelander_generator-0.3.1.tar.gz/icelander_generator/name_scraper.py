"""The scraper of names from wikipedia"""
from __future__ import print_function
from __future__ import unicode_literals
from builtins import object

import json
import os
import requests

from lxml import html


class NameScraper(object):
    """
    NameScraper is made for scraping the icelandic names from wikipedia and dumping them
    into a json file for use in IcelanderGenerator
    """

    WIKI_FORMAT = 'https://is.wikipedia.org/{}'
    WIKI_FEMALES = 'wiki/Listi_yfir_%C3%ADslensk_eiginn%C3%B6fn_kvenmanna'
    WIKI_MALES = 'wiki/Listi_yfir_íslensk_eiginnöfn_karlmanna'
    WIKI_NAME_XPATH = '//div[@id="mw-content-text"]/div/ul/li/a'
    WIKI_GENETIVE_XPATH = '//*[contains(text(), "Eignarfall")]'
    DATA_FOLDER = 'data'
    NAMES_FILE = 'icelandic_names.json'
    NON_GENETIVE_NAMES_FILE = 'non_genetive_names.json'
    names = {
        'female': [],
        'male': []
    }
    non_genetive_names = {
        'female': [],
        'male': []
    }

    def get_name(self, item):
        """Get name for xpath item

        Arguments:
            item {object} -- Xpath object for name

        Returns:
            tuple | None -- Returns tuple with (name, genetive name) or None if genetive name is not found
        """

        url = item.attrib.get('href')
        name = item.text
        genetive_name = name
        name_page = requests.get(self.WIKI_FORMAT.format(url))
        name_page_tree = html.fromstring(name_page.content)
        try:
            # The xpath should give the <a> element that has the genetive label
            label_element = name_page_tree.xpath(self.WIKI_GENETIVE_XPATH)[0]
            # The element we want is the next cell in the table, thus we need to get the parents sibling
            genetive_name = label_element.getparent().getparent().getchildren()[1].text
        except IndexError:
            return None
        return (name, genetive_name)

    def scrape_wiki_for_names(self):
        """Scrape icelandic wikipedia page for names.
        Should only be used for updating icelandic_names.json file from time to time. As it's a scraper
        that visits multiple wikipedia pages it will take a while to do it's thing.
        """
        for gender, path in [('female', self.WIKI_FEMALES), ('male', self.WIKI_MALES)]:
            page = requests.get(self.WIKI_FORMAT.format(path))
            tree = html.fromstring(page.content)
            items_in_name_xpath = tree.xpath(self.WIKI_NAME_XPATH)[0:-2]
            for item in items_in_name_xpath:
                name = self.get_name(item)
                if name is None:
                    name = item.text
                    print('No genetive version found. Not adding {} to names'.format(name))
                    self.non_genetive_names[gender].append(name)
                    continue
                print('Adding: ({}, {}) to {} names'.format(name[0], name[1], gender))
                self.names[gender].append(name)

    def save_names_to_file(self):
        """Saves names to a json file
        """
        file_path = os.path.dirname(__file__)
        with open(os.path.join(file_path, self.DATA_FOLDER, self.NAMES_FILE), 'w') as outfile:
            json.dump(self.names, outfile, indent=2)

        with open(os.path.join(file_path, self.DATA_FOLDER, self.NON_GENETIVE_NAMES_FILE), 'w') as outfile:
            json.dump(self.non_genetive_names, outfile, indent=2)

    def update_names(self):
        """Scrapes all the names and dumps them to the json file
        """

        self.scrape_wiki_for_names()
        self.save_names_to_file()

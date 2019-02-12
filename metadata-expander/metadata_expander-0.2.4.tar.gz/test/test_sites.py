import unittest
import os
from os.path import isfile, join
from importlib import import_module

from bs4 import BeautifulSoup

import sbrowser

from metadata_expander.custom_exceptions import DocumentNotFound

LINKS = {
    'acm': 'https://dl.acm.org/citation.cfm?doid=3178876.3186000',
    'elsevier': 'https://linkinghub.elsevier.com/retrieve/pii/S0001691815300068',
    'google': 'https://scholar.google.de/scholar?hl=de&as_sdt=0%2C5&q=HighLife%3A+Higher-arity+Fact+Harvesting&btnG=',
    'ieee': 'https://ieeexplore.ieee.org/document/4352963',
    'iospress': 'https://content.iospress.com/articles/work/wor1-1-09',
    'springer': 'https://link.springer.com/article/10.1007%2Fs00421-008-0955-8',
    'theiet': 'http://digital-library.theiet.org/content/journals/10.1049/iet-ipr.2015.0467',
    'tib': 'https://www.tib.eu/en/search/id/emerald%3Adoi~10.1108%252F02640470610689151/Digital-object-identifier-system-an-overview/',
    'unitrier': 'https://dblp.uni-trier.de/search?q=HighLife%3A+Higher-arity+Fact+Harvesting'
}


class TestSites(unittest.TestCase):

    def setUp(self):
        self.path = join(os.path.dirname(os.path.realpath(__file__)), "../metadata_expander/sites")
        self.files = [f for f in os.listdir(self.path) if isfile(join(self.path, f))]
        self.files.remove("__init__.py")
        self.files.remove("landing_page.py")
        self.hostnames = [f[:-3] for f in self.files]

    def test_module_callable(self):
        methods = ["def get_bibtex(self)", "def get_dict(self)"]
        for filename in self.files:
            f = open(join(self.path, filename), 'r')
            content = f.read()
            f.close()
            self.assertTrue(methods[0] in content or methods[1] in content,
            msg="[test_sites.test_module_callable] Module %s misses a method. See sites/example.py" % filename)

    def test_getContent(self):
        for hostname in self.hostnames:
            # to many queries and google denies access
            if hostname == "example" or hostname == "google":
                continue

            module_name = hostname[0].upper() + hostname[1:]
            module = getattr(import_module('{}.{}'.format('metadata_expander.sites', hostname)), module_name)()
            link = LINKS[hostname]
            if link:
                soup = BeautifulSoup(sbrowser.goto(link), 'html.parser')
                result = module.get_content(link, soup)
                self.assertGreater(len(result), 2, "[test_sites.test_get_content] Module %s did not return enough results" % module_name)

    def test_DocumentNotFound(self):
        module = getattr(import_module('{}.{}'.format('metadata_expander.sites', "unitrier")), "Unitrier")()
        link = "https://dblp.uni-trier.de/search?q=asdfsdfjkjkj"
        soup = BeautifulSoup(sbrowser.goto(link), 'html.parser')
        self.assertRaises(DocumentNotFound, module.get_content, link, soup)

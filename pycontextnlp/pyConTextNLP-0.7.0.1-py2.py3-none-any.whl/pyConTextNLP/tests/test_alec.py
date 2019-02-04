import sys
print(sys.path)

import unittest
from pyConTextNLP.ConTextMarkup import ConTextMarkup
import pyConTextNLP.itemData as itemData
from pyConTextNLP.itemData import contextItem

class pyConTextNLP_test(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory


        self.su1 = "she states that her surgical incisions are healing well."
        self.su2 = "no prior chronic steroids, dm or other risks for impaired healing beyond obesity."
        self.su3 = "she states that her surgical incisions are healing well."
        self.items = [ ["healed",
                        "NEGATED SUPERFICIAL SURGICAL SITE INFECTION",
                        r"\bheal(ed|ing)\b",
                        ""]]
        self. modifiers = itemData.get_items(
            "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/lexical_kb_05042016.yml")
        self.targets = itemData.get_items(
    "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/utah_crit.yml")


    def tearDown(self):
        self.su1 = ""
        self.su2 = ""
        self.su3 = ""
        self.items = []
    def test_setRawText(self):
        context = ConTextMarkup()
        context.setRawText(self.su1)
        assert context.getRawText() == self.su1
    def test_scrub_preserve_unicode(self):
        context = ConTextMarkup()
        context.setRawText(self.su1)
        context.cleanText(stripNonAlphaNumeric=True)
        # assert context.getText().index(u'\xf6') == 40
    def test_scrub_text(self):
        context = ConTextMarkup()
        context.setRawText(self.su2)
        context.cleanText(stripNonAlphaNumeric=True)
        assert context.getText().rfind(u'.') == -1
    def test_markup_heal(self):
        targets = \
                self.modifiers.append(contextItem(self.items[0]))

        markup = ConTextMarkup()
        markup.setRawText(self.su1)
        markup.cleanText()
        markup.markItems(targets, mode="target")
        markup.pruneMarks()
        markup.dropMarks('Exclusion')
        assert True

if __name__ == '__main__':
    tester = pyConTextNLP_test()
    tester.setUp()
    tester.test_markup_heal()

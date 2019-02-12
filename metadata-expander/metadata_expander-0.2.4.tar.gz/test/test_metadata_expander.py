import unittest

import metadata_expander

solution = {'numpages': '10', 'author': 'Ernst, Patrick and Siu, Amy and Weikum, Gerhard', 'acmid': '3186000', 'ID': 'Ernst:2018:HHF:3178876.3186000', 'publisher': 'International World Wide Web Conferences Steering Committee', 'keywords': 'distant supervision, health, higher-arity relation extraction, knowledge base construction, knowledge graphs, partial facts, text-based knowledge harvesting, tree pattern learning', 'doi': '10.1145/3178876.3186000', 'ENTRYTYPE': 'inproceedings', 'series': "WWW '18", 'pages': '1013--1022', 'title': 'HighLife: Higher-arity Fact Harvesting', 'isbn': '978-1-4503-5639-8', 'booktitle': 'Proceedings of the 2018 World Wide Web Conference', 'url': 'https://doi.org/10.1145/3178876.3186000', 'location': 'Lyon, France', 'year': '2018', 'address': 'Republic and Canton of Geneva, Switzerland'}


class TestMetadataExpander(unittest.TestCase):

    def compare_result(self, result):
        self.assertEqual(solution['title'], result['title'])
        self.assertIn("Ernst", result['author'])
        self.assertIn("Patrick", result['author'])
        self.assertGreater(len(result), 2)

    def test_search_doi(self):
        result = metadata_expander.search_doi(solution['doi'])
        self.compare_result(result)

    def test_search_string(self):
        result = metadata_expander.search_string(solution['title'])
        self.compare_result(result)

    def test_search_meta(self):
        # only use title and year
        meta = {'title': solution['title'], 'year': solution['year']}
        result = metadata_expander.search_meta(meta)
        self.compare_result(result)

        # add doi
        meta['identifier'] = solution['doi']
        result = metadata_expander.search_meta(meta)
        self.compare_result(result)

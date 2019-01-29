import unittest
import requests


# TODO: this should be set once the new rewrite rules are in
# SERVER = "http://w3id.org/biolink/"
SERVER = "http://localhost:8081/biolink/"

# Taken from Firefox network.http.accept.default
default_header = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
github_io = "https://biolink.github.io/biolinkml/"


class RewriteRuleTestCase(unittest.TestCase):

    def rule_test(self, url: str, expected: str, header: str=None) -> None:
        if not header:
            header = default_header
        resp = requests.head(SERVER + url, headers={'accept':header})
        self.assertEqual(302, resp.status_code)
        self.assertEqual(expected, resp.headers['location'])


    def test_model_types(self):
        """ Test the various type(s) rules """
        types_model = 'biolinkml/types'
        self.rule_test(types_model, github_io + 'includes/types.html')
        # self.rule_test(types_model + '.foo', github_io + 'includes/types.html')
        self.rule_test(types_model, github_io + 'includes/types.yaml', 'text/yaml')
        self.rule_test(types_model, github_io + 'includes/types.yaml', 'text/yaml,' + default_header)
        self.rule_test(types_model, github_io + 'includes/types.ttl', 'text/turtle,' + default_header)
        self.rule_test(types_model, github_io + 'includes/types.json', 'application/json,' + default_header)

    def test_model_files(self):
        """ Make sure that the model files can be retrieved in the correct formats """
        resp = requests.head("http://localhost:8081/biolink/biolinkml/meta", headers={'accept': "text/html"})
        self.assertEqual(302, resp.status_code)
        self.assertEqual("https://biolink.github.io/biolinkml/meta.html", resp.headers['location'])



if __name__ == '__main__':
    unittest.main()

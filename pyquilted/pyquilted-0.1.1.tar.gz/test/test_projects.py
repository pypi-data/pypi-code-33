import unittest
from pyquilted.quilted.projects import *


class TestProjects(unittest.TestCase):
    def test_projects(self):
        data = {
                'name': 'Wight Hunt',
                'description': 'Lead a small team north to capture a wight alive',
                'flair': 'S7E06 Beyond the Wall',
                'flair_icon': 'fa-film',
                'slugs': ['Mission complete', 'Saved by my uncle']
                }
        activity = Activity(**data)
        projects = Projects()
        projects.add_activity(activity)
        valid = {
                'projects': {
                    'label': 'Projects',
                    'icon': 'fa-code',
                    'blocks': [{
                        'name': 'Wight Hunt',
                        'description': 'Lead a small team north to capture a wight alive',
                        'flair': 'S7E06 Beyond the Wall',
                        'flair_icon': 'fa-film',
                        'slugs': ['Mission complete', 'Saved by my uncle']
                    }]
                }}
        self.assertEqual(projects.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

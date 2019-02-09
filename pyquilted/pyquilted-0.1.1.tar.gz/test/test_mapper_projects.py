import unittest
from pyquilted.mapper.projects import ProjectsMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperProjects(unittest.TestCase):
    def test_mapper_projects(self):
        with open('tests/validations/projects.yml') as f:
            data = YamlLoader.ordered_load(f)
        mapper = ProjectsMapper(data['projects'])
        projects = mapper.deserialize()

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

import unittest
from pyquilted.mapper.heading import HeadingMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperHeading(unittest.TestCase):
    def test_mapper_heading(self):
        with open('tests/validations/heading.yml') as f:
            odata = YamlLoader.ordered_load(f)
        mapper = HeadingMapper(odata['heading'])
        heading = mapper.deserialize()

        valid = {
                'name': 'Jon Snow',
                'title': 'The White Wolf',
                'location': 'Winterfell',
                'via': 'fa-motorcycle'
                }
        self.assertEqual(heading.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

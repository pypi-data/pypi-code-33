import unittest
from pyquilted.mapper.work import WorkMapper
from pyquilted.yaml_loader import YamlLoader


class TestMapperWork(unittest.TestCase):
    def test_mapper_work(self):
        with open('tests/validations/work.yml') as f:
            data = YamlLoader.ordered_load(f)
        mapper = WorkMapper(data['work'])
        work = mapper.deserialize()

        valid = {
                'work': {
                    'label': 'Work',
                    'icon': 'fa-briefcase',
                    'blocks': [
                        {
                            'dates': 'Jan 2017–Dec 2017',
                            'location': 'The Wall, KoN',
                            'company': 'The Night\'s Watch',
                            'title': 'Lord Commander',
                            'slugs': [
                                'United Wildlings and The Night\'s Watch',
                                'Youngest Lord Commander',
                                'Died for my people yo'
                             ]
                        }]
                    }
                }
        self.assertEqual(work.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

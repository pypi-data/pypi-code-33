import unittest
from pyquilted.quilted.work import *


class TestWork(unittest.TestCase):
    def test_work(self):
        data = {
                'dates': 'Jan 2017–Dec 2017',
                'location': 'The Wall, KoN',
                'company': 'The Night\'s Watch',
                'title': 'Lord Commander',
                'slugs': [
                    'United Wildlings and The Night\'s Watch',
                    'Youngest Lord Commander',
                    'Died for my people yo'
                    ]
                }
        job = Job(**data)
        work = Work()
        work.add_job(job)
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

import unittest
from pyquilted.quilted.heading import Heading


class TestHeading(unittest.TestCase):
    def test_heading(self):
        heading = Heading(
                name="Jon Snow",
                title="King in the North",
                location="Winterfell",
                via="subway")
        valid = {
                'name': 'Jon Snow',
                'title': 'King in the North',
                'location': 'Winterfell',
                'via': 'fa-subway'
                }
        self.assertEqual(heading.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

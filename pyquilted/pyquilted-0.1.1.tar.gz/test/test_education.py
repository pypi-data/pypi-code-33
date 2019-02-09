import unittest
from pyquilted.quilted.education import Education


class TestEducation(unittest.TestCase):
    def test_education(self):
        education = Education('The Night\'s Watch')
        valid = {
                "education": {
                    "label": "Education",
                    "value": "The Night's Watch",
                    "icon": "fa-graduation-cap"
                    }
                }
        self.assertEqual(education.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

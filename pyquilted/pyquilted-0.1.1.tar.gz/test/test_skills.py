import unittest
from pyquilted.quilted.skills import Skills


class TestSkills(unittest.TestCase):
    def test_skills(self):
        skills= Skills([
            'Brooding', 'Knowing-nothing', 'Leadership', 'Swooning',
            'Swordsmanship','HTML' ])

        valid = {
                "skills": {
                    "label": "Skills",
                    "value": "Brooding, Knowing-nothing, Leadership, Swooning, Swordsmanship, HTML",
                    "icon": "fa-wrench"
                    }
                }
        self.assertEqual(skills.serialize(), valid)


if __name__ == '__main__':
    unittest.main()

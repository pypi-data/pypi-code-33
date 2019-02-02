from yo_extensions.misc import *
from tests.extensions.common import *
from IPython.display import HTML

class MiscTests(TestCase):
    def test_json(self):
        os.makedirs(path('misc_files'),exist_ok=True)
        jsonpath = path('misc_files','test.json')
        obj = dict(a=1,b='2')
        save_json(jsonpath,obj)
        self.assertDictEqual(
            dict(a=1,b='2'),
            load_json(jsonpath))

    def test_json_1(self):
        jsonpath = path('misc_files', 'test1.json')
        obj = dict(a=1, b='2')
        save_json(jsonpath, obj)
        self.assertDictEqual(
            dict(a=1, b='2'),
            load_json(jsonpath,as_obj=True))


    def test_pickle(self):
        jsonpath = path('misc_files', 'test.pkl')
        obj = dict(a=1, b='2')
        save_pkl(jsonpath, obj)
        self.assertDictEqual(
            dict(a=1, b='2'),
            load_pkl(jsonpath))

    def test_printable(self):
        self.assertIsInstance(notebook_printable_version(True),HTML)
        self.assertIsNone(notebook_printable_version(False))

    def test_find_root_fails(self):
        self.assertRaises(ValueError,lambda: find_root_folder('aigjixfjbvijfdawemnarldsncolkcznvoisalmenfwsefdfsdvlskdapejr'))
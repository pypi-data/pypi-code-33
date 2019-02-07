from looqbox.objects.tests import ObjTable
from looqbox.objects.tests import LooqObject
import unittest
import json
import numpy as np
import pandas as pd

class TestObjectTable(unittest.TestCase):
    """
    Test looq_table file
    """

    def test_instance(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        self.assertIsInstance(looq_object_table, LooqObject)

    def test_json_creation(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON keys
        json_keys = list(json.loads(looq_object_table.to_json_structure).keys())
        self.assertEqual(json_keys, ["objectType", "title", "header", "body", "footer", "searchable", "searchString",
                                     "paginationSize", "framed", "framedTitle", "stacked", "showBorder",
                                     "showOptionBar", "showHighlight", "striped", "sortable", "class"],
                         msg="Failed basic JSON structure test")

    def test_header_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON header keys
        json_table = json.loads(looq_object_table.to_json_structure)
        self.assertEqual(list(json_table["header"].keys()), ["content", "visible", "group"],
                         msg="Failed basic header JSON structure test")

    def test_body_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON body keys
        json_table = json.loads(looq_object_table.to_json_structure)
        self.assertEqual(list(json_table["body"].keys()), ["content", "format", "class"],
                         msg="Failed basic body JSON structure test")

    def test_footer_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON footer keys
        json_table = json.loads(looq_object_table.to_json_structure)
        self.assertEqual(list(json_table["footer"].keys()), ["content"],
                         msg="Failed basic footer JSON structure test")


if __name__ == '__main__':
    unittest.main()

from looqbox.objects.tests import ObjPlotly
from looqbox.objects.tests import LooqObject
import unittest
import json
import plotly.plotly as py
import plotly.graph_objs as go

class TestObjectPlotly(unittest.TestCase):
    """
    Test looq_plotly file
    """

    def test_instance(self):
        data = [go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23]
        )]

        looq_object_plotly = ObjPlotly(data)

        self.assertIsInstance(looq_object_plotly, LooqObject)

    def test_json_creation(self):
        # Testing JSON keys
        data = [go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23]
        )]

        looq_object_plotly = ObjPlotly(data)
        json_keys = list(json.loads(looq_object_plotly.to_json_structure).keys())
        self.assertEqual(json_keys, ["objectType", "data", "layout", "stacked", "displayModeBar"],
                         msg="Failed basic JSON structure test")


if __name__ == '__main__':
    unittest.main()
3
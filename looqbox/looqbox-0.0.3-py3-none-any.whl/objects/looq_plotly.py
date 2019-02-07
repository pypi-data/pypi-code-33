from looqbox.objects.looq_object import LooqObject
import json
import plotly.graph_objs as go


class ObjPlotly(LooqObject):
    def __init__(self, data, layout=None, stacked=True, display_mode_bar=True):
        """
            :param data: Plotly general values. Can be a dict or a plotly object like Bar, Scatter and etc..

            :param layout: Layout elements of the plotly, it's a Layout object from plotly.graph_objs,
            if it's not send as parameter, the function creates it internally

            :param display_mode_bar: Show mode bar in the plotly visualization
        """
        super().__init__()
        self.data = data
        self.layout = layout
        self.stacked = stacked
        self.display_mode_bar = display_mode_bar

    @property
    def to_json_structure(self):
        """
        Create the Plotly JSON structure to be read in the FES.
          In this case the function has some peculiarities, for example, if the plotly object has some field of special
          types like ndarray, datetime and etc.. the json's convertion will break because these types objects are not
          serializable. Because of this, before sent the ObjectPlotly to the response frame, the programmer needs to
          transform these fields into normal lists.
            Example:
                nparray = nparray.tolist()

        :return plotly_json
        """
        if self.layout is None:
            self.layout = go.Layout()

        figure = go.Figure(data=self.data, layout=self.layout)
        figure_json = figure.to_plotly_json()

        json_content = {'objectType': 'plotly',
                        'data': json.dumps(figure_json['data']),
                        'layout': json.dumps(figure_json['layout']),
                        'stacked': self.stacked,
                        'displayModeBar': self.display_mode_bar
                        }

        plotly_json = json.dumps(json_content, indent=1)

        return plotly_json

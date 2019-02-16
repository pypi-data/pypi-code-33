from .util import Util


class BuilderParams:
    """
    Validating input parameters and building jsons for chart init

    -----
    Attributes:

    obj: a Chart object whose attributes will be checked and built by BuilderParams.
    """

    def __init__(self,
                 obj):
        """
        """
        self.obj = obj

    def valid(self):
        """
        Checks if the values for the given entries are valid.
        """
        msg = 'width must be an int (number of pixels) or a string'
        assert (isinstance(self.obj.width_in, int)
                or isinstance(self.obj.width_in, str)), msg

        msg = 'height must be an int (number of pixels)'
        assert isinstance(self.obj.height_in, int), msg

        li_theme = ['dark-unica',
                    'grid-light',
                    'sand-signika',
                    '']
        # Empty string is a valid theme
        msg = 'theme must be one of {}'.format(li_theme)
        assert self.obj.theme in li_theme, msg

        msg = 'options must be a dict'
        assert isinstance(self.obj._options_dict, dict), msg

        msg = 'data must be a list'
        assert isinstance(self.obj.data_in, list), msg

    def build(self):
        """
        Builds parameters of the chart
        """

        # Convert width to string
        if isinstance(self.obj.width_in, int):
            self.obj.width = str(self.obj.width_in) + 'px'
        else:
            self.obj.width = self.obj.width_in

        # Height
        if self.obj.height_in == 0:
            self.obj.height_in = 350
        self.obj.height = str(self.obj.height_in) + 'px'

        # Options
        options, data = self.preprocess_input(
            self.obj._options_dict, self.obj.data_in)

        self.obj._options_down = Util.build_options(options)

        self.obj._data_down = Util.build_data(data)

    def preprocess_input(self, options, data):
        """
        Adds options and correct data according to the required parameters.
        """

        return options, data

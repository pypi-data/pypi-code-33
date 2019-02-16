from copy import copy, deepcopy
import random
import os
import pandas as pd
import simplejson as json

import ipywidgets as wg

from traitlets import observe, Unicode, Dict, List, Int, Bool

from .builder_param import BuilderParams
from .__meta__ import __version_js__

_semver_range_frontend_ = '~' + __version_js__


class Chart(wg.DOMWidget):
    """
    HighCharts Widget.

    -----
    Attributes:

    TBD
    """
    _model_name = Unicode('ChartModel').tag(sync=True)
    _view_name = Unicode('ChartView').tag(sync=True)
    _model_module = Unicode('ipyhc').tag(sync=True)
    _view_module = Unicode('ipyhc').tag(sync=True)
    _view_module_version = Unicode(_semver_range_frontend_).tag(sync=True)
    _model_module_version = Unicode(_semver_range_frontend_).tag(sync=True)

    _id = Int(0).tag(sync=True)

    theme = Unicode('').tag(sync=True)
    width = Unicode('').tag(sync=True)
    height = Unicode('').tag(sync=True)
    stock = Bool(False).tag(sync=True)
    update_data = Int(0).tag(sync=True)

    _options_down = Unicode('').tag(sync=True)
    _data_down = Unicode('').tag(sync=True)
    _data_up = Unicode('').tag(sync=True)

    def __init__(self,
                 width='100%',
                 height=0,
                 theme='',
                 stock=False,
                 options={},
                 data=[],
                 unsync=False):
        """
        Instantiates the widget. See TBD
        for more details.
        """

        self._id = random.randint(0, int(1e9))
        self.width_in = width
        self.height_in = height
        self.theme = theme
        self.stock=stock
        self._options_dict = options
        self.data_in = deepcopy(data)
        self.update_data = 0
        self.data_out = {'counter':0}
        self.unsync=unsync

        bp = BuilderParams(self)
        bp.valid()
        bp.build()

        super().__init__()
    
    @observe('_data_up')
    def export(self, change):
        if not self.unsync:
            self.data_out = json.loads(self._data_up)
            self.update_data +=1

import json
from copy import deepcopy as copy

from .div import Div
from .title import Title
from .tab import Tab
from .list_js import ListJs
from .misc import Misc
from .header import Header


class Dashboard:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Dashboard'
        self.title = None
        self.tabs = []
        self.css = None
        self.js = None
        self.misc = None
        self.header = None
        self.markdown = None
        self.widgets = False
        self.widgets_state = None
        self.latex = None

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

        self.build_widgets_state()

    def check(self, verbose=False):
        isTitle = (self.title is None) or isinstance(self.title, Title)
        isTabs = isinstance(self.tabs, list) and all(
            isinstance(e, Tab) for e in self.tabs)
        isJs = isinstance(self.js, ListJs)
        isMisc = isinstance(self.misc, Misc)
        isExactlyOneActiveTab = sum([1 for e in self.tabs if e.active]) == 1
        isHeader = isinstance(self.header, Header) or self.header is None
        isMarkdown = isinstance(self.markdown, bool)
        isWidgets = isinstance(self.widgets, bool)
        isWidgetsState = isinstance(
            self.widgets_state, list) and all(
            isinstance(e, dict) for e in self.widgets_state)
        isLatex = isinstance(self.latex, bool)
        isDashboard = isTitle and isTabs and isMisc and isExactlyOneActiveTab \
            and isHeader and isMarkdown and isWidgets and isLatex
        if verbose:
            print('Dashboard: isTitle=', isTitle)
            print('Dashboard: isTabs=', isTabs)
            print('Dashboard: isJs=', isJs)
            print('Dashboard: isMisc=', isMisc)
            print('Dashboard: isExactlyOneActiveTab=', isExactlyOneActiveTab)
            print('Dashboard: isHeader=', isHeader)
            print('Dashboard: isMarkdown=', isMarkdown)
            print('Dashboard: isWidgets=', isWidgets)
            print('Dashboard: isWidgetsState=', isWidgetsState)
            print('Dashboard: isLatex=', isLatex)
            print('Dashboard: isDashboard=', isDashboard)
        msg = 'Dashboard attributes title, tabs, css, js, misc must be objects ' + \
              'resp. Title, list(Tab), str, ListJs, Misc, Header, list(Div), bool. ' + \
              'There must be exactly one active tab'
        assert isDashboard, msg

        return True

    def build_widgets_state(self):
        """
        """
        if self.widgets_state and len(self.widgets_state):
            d0 = self.widgets_state[0]
            for d in self.widgets_state[1:]:
                d0['state'].update(d['state'])
            self.widgets_state = d0
            self.widgets_state = json.dumps(self.widgets_state)
        else:
            self.widgets_state = ''

    def to_dict(self, short=False):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        for k, v in d.items():
            if isinstance(v, (Title, Misc)):
                d[k] = v.to_dict()
            elif isinstance(v, Header):
                d[k] = v.to_dict(short=short)
            elif isinstance(v, ListJs):
                d[k] = v.to_list()
            elif isinstance(v, (str, bool)):
                d[k] = v
            elif isinstance(v, list):
                v2 = []
                for e in v:
                    if isinstance(e, (Tab, Div)):
                        v2.append(e.to_dict())
                d[k] = v2
        return d

    def pprint(self, indent=2):
        d = self.to_dict(short=True)
        d = json.dumps(d, sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())

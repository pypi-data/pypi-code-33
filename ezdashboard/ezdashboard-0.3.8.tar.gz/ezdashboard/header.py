
import os
import json
import base64

from copy import deepcopy as copy


class Header:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Header'
        self.left_logo = None
        self.left_title = None
        self.right_logo = None
        self.toggle = False

        self.left_logo_img_src = None
        self.right_logo_img_src = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.valid = self.check(verbose=verbose)
        self.build_img()

    def check(self, verbose=False):
        left_ok = (isinstance(self.left_logo, str) and
                   os.path.exists(self.left_logo)) or self.left_logo is None
        right_ok = (isinstance(self.right_logo, str)
                    and os.path.exists(self.right_logo)) or self.right_logo is None
        isTitle = isinstance(self.left_title, str) or self.left_title is None
        isToggle = isinstance(self.toggle, bool)

        isHeader = all([left_ok, right_ok, isTitle, isToggle])
        if verbose:
            print('Header: left_ok=', left_ok)
            print('Header: right_ok=', right_ok)
            print('Header: isTitle=', isTitle)
            print('Header: isToggle=', isToggle)
        msg = 'Header attributes if defined must be strings - preferably representing img paths and text'
        assert isHeader, msg

        return True

    def build_img(self):
        if self.left_logo:
            data_uri = base64.b64encode(open(self.left_logo, 'rb').read()).decode(
                'utf-8').replace('\n', '')
            self.left_logo_img_src = 'data:image/png;base64,{0}'.format(
                data_uri)

        if self.right_logo:
            data_uri = base64.b64encode(open(self.right_logo, 'rb').read()).decode(
                'utf-8').replace('\n', '')
            self.right_logo_img_src = 'data:image/png;base64,{0}'.format(
                data_uri)

    def to_dict(self, short=False, n=250):
        d = copy(self.__dict__)
        if short:
            for k in ['left_logo_img_src', 'right_logo_img_src']:
                e = d[k]
                d[k] = e[:n] + '...' + \
                    '({} more characters)'.format(len(e) - n)
        return d

    def pprint(self, indent=2):
        d = self.to_dict(short=True)
        d = json.dumps(d, sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        d = str(self.to_dict())
        return d

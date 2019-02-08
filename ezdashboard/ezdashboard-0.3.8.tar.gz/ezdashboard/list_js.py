
import json
from copy import deepcopy as copy


class ListJs:

    def __init__(self, li_js_lib, verbose=False):
        """
        TBD
        """
        # attributes
        self.type = 'ListJs'
        self.li_js_lib = li_js_lib

        self.valid = self.check(verbose=verbose)

    def check(self, verbose=False):

        isList = isinstance(self.li_js_lib, list)
        isJsStr = all((isinstance(e, str)) for e in self.li_js_lib)
        isListJs = isList and isJsStr
        if verbose:
            print('ListJs: isList=', isList)
            print('ListJs: isJsStr=', isJsStr)
            print('ListJs: isListJs=', isListJs)
            
        msg = 'ListJs must be a list of strings, possibly empty' + \
              'each representing the url of a js lib'
        assert isListJs, msg

        return True

    def pprint(self, indent=2):
        d = json.dumps(self.to_list(), sort_keys=True, indent=indent)
        print(d)

    def to_list(self):
        d = copy(self.li_js_lib)
        return d

    def __repr__(self):
        return str(self.to_list())

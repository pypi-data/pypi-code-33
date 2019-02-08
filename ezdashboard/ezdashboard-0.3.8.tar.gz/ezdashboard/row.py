
import json
from copy import deepcopy as copy

from .list_div import ListDiv


class Row:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Row'
        self.id_name = None
        self.class_name = None
        self.elmts = None

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

    def check(self, verbose=False):
        isRow = isinstance(self.elmts, ListDiv)
        if verbose:
            print('Rows: isRow=', isRow)
        msg = 'Row must contain a ListDiv instance'
        assert isRow, msg

        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        for k, v in d.items():
            if isinstance(v, ListDiv):
                d[k] = v.to_dict()
        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())

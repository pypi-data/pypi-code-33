import json
from copy import deepcopy as copy

from .div import Div

class ListDiv:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'ListDiv'
        self.id_name = None
        self.class_name = None
        self.width = 12
        self.elmts = []
        self.level = 1

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

    def check(self, verbose=False):
        isListDivLevel1 = isinstance(self.elmts, list) and all(
            (isinstance(e, (Div, ListDiv))) for e in self.elmts)
        isListDivLevel2 = isinstance(self.elmts, list) and all(
            (isinstance(e, Div)) for e in self.elmts)
        isListDiv = (self.level == 1 and isListDivLevel1) or (
            self.level == 2 and isListDivLevel2)
        if verbose:
            print('ListDiv: isListDivLevel1=', isListDivLevel1)
            print('ListDiv: isListDivLevel2=', isListDivLevel2)
            print('ListDiv: isListDiv=', isListDiv)
        msg = 'ListDiv must contain a list of Div or ListDiv instances only'
        assert isListDiv, msg

        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        for k, v in d.items():
            if isinstance(v, list):
                v2 = []
                for e in v:
                    if isinstance(e, (Div, ListDiv)):
                        v2.append(e.to_dict())
                d[k] = v2
        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())

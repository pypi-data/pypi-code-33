
import json
from copy import deepcopy as copy

from .title import Title
from .row import Row


class Tab:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Tab'
        self.class_name = None
        self.name = None
        self.active = False
        ## rows or tabs
        self.elmts = None
        self.level = 1
        self.keyboard = True

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

        self.keyboard = int(self.keyboard)

    def check(self, verbose=False):
        isLevel = isinstance(self.level, int) and self.level in [1, 2]
        isCandListTab = isinstance(self.elmts, list) and all(
            isinstance(e, Tab) for e in self.elmts)
        isCandListTitleRow = isinstance(self.elmts, list) and all(
            (isinstance(e, Title) or isinstance(e, Row))
            for e in self.elmts)
        nbActiveTab = sum(
            [1 for e in self.elmts if (isinstance(e, Tab) and e.active)])
        isNbActiveTabCorrect = nbActiveTab == 1 if self.elmts[0].type == 'Tab' else True
        isKeyboard = isinstance(self.keyboard, bool)
        isTab = ((isLevel == 2 and isCandListTitleRow) or (
            isLevel == 1 and (isCandListTab or isCandListTitleRow))) and isKeyboard
        isTab = isTab and isNbActiveTabCorrect
        if verbose:
            print('Tab: isLevel=', isLevel)
            print('Tab: isCandListTab=', isCandListTab)
            print('Tab: isCandListTitleRow=', isCandListTitleRow)
            print('Tab: nbActiveTab=', nbActiveTab)
            print('Tab: isKeyboard=', isKeyboard)
            print('Tab: isNbActiveTabCorrect=', isNbActiveTabCorrect)
            print('Tab: isTab=', isTab)
        msg = 'Tab must contain a list of only (Title or Row) or only (Tab) instances (if level=1)\n' + \
              'Tab must contain a list of only (Title or Row) instances (if level=2)\n' +\
              'Only one underlying tab, if any, must be active=True'

        assert isTab, msg

        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        for k, v in d.items():
            if isinstance(v, list):
                v2 = []
                for e in v:
                    if isinstance(e, (Title, Row, Tab)):
                        v2.append(e.to_dict())
                d[k] = v2

        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())

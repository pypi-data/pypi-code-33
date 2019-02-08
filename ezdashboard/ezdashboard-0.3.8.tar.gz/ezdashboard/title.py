
import json
from copy import deepcopy as copy


class Title:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Title'
        self.id_name = None
        self.class_name = None
        self.size = None
        self.text = ''

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

    def check(self, verbose=False):
        isSize = isinstance(self.size, int) and self.size in [1, 2, 3, 4, 5]
        isText = isinstance(self.text, str) and self.text != ''
        isTitle = isSize and isText

        if verbose:
            print('Title: isTitle=', isTitle)
        msg = 'Title must contain size and text'
        assert isTitle, msg
        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())


import json
from copy import deepcopy as copy


class Misc:

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Misc'
        self.main_type = 'container-fluid'
        self.main_nav_width = None
        self.main_nav_min_height = None
        self.main_content_width = None
        self.no_margins = True

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

    def check(self, verbose=False):
        t1 = self.main_type in ['container-fluid', 'container']
        t2 = isinstance(self.main_nav_width,
                        str) or self.main_nav_width is None
        t3 = isinstance(self.main_nav_min_height,
                        str) or self.main_nav_min_height is None
        t4 = isinstance(self.main_content_width,
                        str) or self.main_content_width is None
        t5 = isinstance(self.no_margins,
                        bool) or self.no_margins is None
        isMisc = all([t1, t2, t3, t4, t5])
        if verbose:
            print('Misc: t1=', t1)
            print('Misc: t2=', t2)
            print('Misc: t3=', t3)
            print('Misc: t4=', t4)
            print('Misc: t5=', t5)
            print('Misc: isMisc=', isMisc)
        msg = 'Mics attributes if defined must be strings - preferably representing valid css properties'
        assert isMisc, msg

        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        d = str(self.to_dict())
        return d

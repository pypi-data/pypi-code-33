import builtins
import itertools
from addict import Dict


def format_key(key):
    strip = key.strip('@')
    return '{}_'.format(strip) if strip in itertools.chain(dir(builtins)) else strip


class RossbyResponse(Dict):

    def __init__(self, *args, **kwargs):
        super(RossbyResponse, self).__init__(*args, **kwargs)
        self.response = kwargs.get('response', None)
        self.latest_response = self.response

        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    object.__setattr__(self, format_key(key), self._hook(val))
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                pass
            else:
                for key, val in iter(arg):
                    object.__setattr__(self, format_key(key), self._hook(val))

        for key, val in kwargs.items():
            object.__setattr__(self, key, val)

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, list):
            return type(item)(cls._hook(elem) for elem in item)

        return item

    @property
    def json(self):
        return self.response.json()

    @property
    def next_page(self):
        return self.latest_response.json().get('pagination', {}).get('next', None)

    def paginate(self):
        while self.next_page:
            _page = self.api.request_response(self.next_page, self.endpoint)
            self.latest_response = _page.response

            yield _page

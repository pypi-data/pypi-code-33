
class INamedValues:
    def contains(self, name: str) -> bool:
        raise NotImplementedError()

    # None if does not contain
    def get_raw_value(self, name: str):
        raise NotImplementedError()


class ILocation:
    def get_location(self) -> (str, None):
        raise NotImplementedError()


class StrLocation(ILocation):
    def __init__(self, s: str):
        assert isinstance(s, str), s
        self.str_ = s

    def get_location(self) -> (str, None):
        return self.str_


class NamedParameters:
    def __init__(self, src: INamedValues, exc_type: type = Warning, location: ILocation = None):
        assert isinstance(src, INamedValues), src
        assert isinstance(exc_type, type), exc_type
        assert location is None or isinstance(location, ILocation), location

        self.src_ = src
        self.exc_type_ = exc_type
        self.location_ = location

    def _exc(self, msg: str) -> Exception:
        if self.location_:
            loc = self.location_.get_location()
            if loc:
                assert isinstance(loc, str), loc
                return self.exc_type_(loc + ': ' + msg)

        return self.exc_type_(msg)

    def get_raw(self, name: str, allow_none: bool = False, optional: bool = False, default=None):
        assert isinstance(name, str), name
        assert isinstance(allow_none, bool), allow_none
        assert isinstance(optional, bool), optional

        if not self.src_.contains(name):
            if optional:
                return default
            raise self._exc('Parameter {} is missing'.format(name))

        v = self.src_.get_raw_value(name)
        if v is None and not allow_none:
            raise self._exc('Parameter {} is None'.format(name))
        return v

    # options should consist of str. None should not be put there
    def get_str(self, name: str, allow_none: bool = False, optional: bool = False, default: str = None, options: (list, tuple) = None) -> (str, None):
        assert isinstance(name, str), name
        assert isinstance(allow_none, bool), allow_none
        assert isinstance(optional, bool), optional
        assert default is None or isinstance(default, str), default
        assert options is None or isinstance(options, (list, tuple)), options

        if not self.src_.contains(name):
            if optional:
                return default
            raise self._exc('Parameter {} is missing'.format(name))

        v = self.src_.get_raw_value(name)
        if v is None:
            if allow_none:
                return None
            raise self._exc('Parameter {} is None'.format(name))

        if not isinstance(v, str):
            raise self._exc('Parameter {}={} should be str, not {}'.format(name, v, type(v)))

        if options and v not in options:
            raise self._exc('Parameter {}={} is invalid, available values: {}'.format(name, v, options))

        return v

    def get_bool(self, name: str, allow_none: bool = False, optional: bool = False, default: bool = None) -> (bool, None):
        assert isinstance(name, str), name
        assert isinstance(allow_none, bool), allow_none
        assert isinstance(optional, bool), optional
        assert default is None or isinstance(default, bool), default

        if not self.src_.contains(name):
            if optional:
                return default
            raise self._exc('Parameter {} is missing'.format(name))

        v = self.src_.get_raw_value(name)
        if v is None:
            if allow_none:
                return None
            raise self._exc('Parameter {} is None'.format(name))

        if not isinstance(v, bool):
            raise self._exc('Parameter {}={} should be bool, not {}'.format(name, v, type(v)))

        return v

    def get_int(self, name: str, allow_none: bool = False, optional: bool = False, default: int = None) -> (str, None):
        assert isinstance(name, str), name
        assert isinstance(allow_none, bool), allow_none
        assert isinstance(optional, bool), optional
        assert default is None or isinstance(default, int), default

        if not self.src_.contains(name):
            if optional:
                return default
            raise self._exc('Parameter {} is missing'.format(name))

        v = self.src_.get_raw_value(name)
        if v is None:
            if allow_none:
                return None
            raise self._exc('Parameter {} is None'.format(name))

        if not isinstance(v, int):
            raise self._exc('Parameter {}={} should be int, not {}'.format(name, v, type(v)))

        return v

    def get_dict(self, name: str, dic: dict, optional: bool = False, default=None):
        assert isinstance(name, str), name
        assert isinstance(dic, dict), dic
        assert isinstance(optional, bool), optional

        if not self.src_.contains(name):
            if optional:
                return default
            raise self._exc('Parameter {} is missing'.format(name))

        v = self.src_.get_raw_value(name)

        if v in dic:
            return dic[v]
        else:
            raise self._exc('Attribute "{}={}" is invalid. Available values: {}'.format(name, v, dic.keys()))


class DictReader(NamedParameters, INamedValues):
    def __init__(self, d: dict, exc_type=Warning, location: ILocation = None):
        assert isinstance(d, dict), d

        super().__init__(self, exc_type, location)

        self.d_ = d

    def contains(self, name: str) -> bool:
        return name in self.d_

    # None if does not contain
    def get_raw_value(self, name: str):
        return self.d_.get(name)

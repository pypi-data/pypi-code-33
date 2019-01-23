import six

from .document_manager import DocumentManager


class DocumentMeta(type):
    def __init__(self, name, bases, fields):
        super(DocumentMeta, self).__init__(name, bases, fields)
        self.objects = DocumentManager(self)


class DocumentCommonMixIn(object):
    def _fix(self, obj, options={}):
        if hasattr(obj, 'json'):
            return obj.json(**options)

        elif isinstance(obj, list):
            return list(map(
                lambda x: x.json(**options) if hasattr(x, 'json') else x,
                obj
            ))
        return obj

    def _resolve(self, result, fld):
        if isinstance(fld, dict):
            for fld2, fld_options in fld.items():
                result[fld2] = self._fix(self.get(fld2), fld_options)
        else:
            result[fld] = self._fix(self.get(fld))

    def json(self, resolve=None, exclude=None):
        result = {}
        result.update(self._data)
        if '__ver' in result:
            result.pop('__ver')

        if resolve:
            for fld in resolve:
                self._resolve(result, fld)

        if exclude:
            for fld in exclude:
                if fld in result:
                    result.pop(fld)

        return result


@six.add_metaclass(DocumentMeta)
class Document(DocumentCommonMixIn):
    __collection__ = None
    __history_collection__ = None

    __version__ = '1.0.0'
    __fields__ = []
    __resolve__ = {}
    __reverse__ = {}
    __autos__ = {}

    __attr_exceptions = ('_data', '_dirty', '_changed')
    __attr_allow = ('_id', '__ver')

    @classmethod
    def set_collection(cls, collection, history_collection=None):
        cls.__collection__ = collection
        cls.__history_collection__ = history_collection

    def __init__(self, **kwargs):
        self._data = {}
        self._data['__ver'] = self.__version__
        self._dirty = '_id' not in kwargs
        self._changed = {}

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get(self, name):
        return getattr(self, name)

    def __getattr__(self, name):
        if name in self.__attr_exceptions:
            return super(Document, self).__getattribute__(name)

        elif name in self.__resolve__:
            fld, klass, key = self.__resolve__[name]
            if fld == '__inline__':
                res = klass(self, name)
                return res
            else:
                if fld in self._data and self._data[fld] is not None:
                    val = self._data[fld]
                    if isinstance(val, list):
                        result = []
                        for v in val:
                            result.append(klass.objects.find_one(**{key: v}))
                        return result
                    else:
                        return klass.objects.find_one(**{key: self._data[fld]})
                else:
                    return None

        elif name in self.__fields__ or name in self.__attr_allow:
            return self._data.get(name)

        elif name in self.__reverse__:
            fld, klass = self.__reverse__[name]
            klass = klass()
            return klass.objects.find(**{fld: self._id})

        return super(Document, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name in self.__attr_exceptions:
            return super(Document, self).__setattr__(name, value)

        if name in self.__fields__ or name in self.__attr_allow:
            self._data[name] = value
            self._changed[name] = value
            self._dirty = True

        elif name in self.__resolve__:
            fld, klass, key = self.__resolve__[name]
            if not isinstance(value, klass):
                raise ValueError
            self._data[fld] = value.get(key)
            self._changed[name] = value.get(key)
        # else:
        #     raise AttributeError

    def __repr__(self):
        return '%s(**%s)' % (self.__class__.__name__, repr(self._data))

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs).save(force_create=True)

    def delete(self):
        self.objects.delete(self._id)

    def save(self, force=False, force_create=False, skip_autos=False):
        if not skip_autos:
            for k, v in self.__autos__.items():
                self._data[k] = v()

        if '_id' in self._data and not force_create:
            if not self._dirty and not force:
                return self
            self.objects.update(self._data)
        else:
            self.objects.insert(self._data)

        self._dirty = False

        return self


class MiniDocument(DocumentCommonMixIn):
    __collection__ = None

    __fields__ = []
    __resolve__ = {}
    __reverse__ = {}
    __autos__ = {}

    __attr_exceptions = ('_parent', '_name')
    __attr_allow = ('_id', '__ver')

    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def get(self, name):
        return getattr(self, name)

    def update(self, other):
        for k, v in other.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        if name in self.__attr_exceptions:
            return super(MiniDocument, self).__getattr__(name)

        if name in self.__fields__ or name in self.__attr_allow:
            return self._parent._data.get(self._name, {}).get(name)

        elif name in self.__resolve__:
            fld, klass, key = self.__resolve__[name]
            if fld in self._parent._data.get(self._name, {}):
                return klass.objects.find_one(
                    **{key: self._parent._data.get(self._name, {})[fld]})
            else:
                return None

        elif name in self.__reverse__:
            fld, klass = self.__reverse__[name]
            klass = klass()
            return klass.objects.find(**{fld: self._id})

        return super(MiniDocument, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name in self.__attr_exceptions:
            return super(MiniDocument, self).__setattr__(name, value)

        if name in self.__fields__ or name in self.__attr_allow:
            self._parent._data.setdefault(self._name, {})[name] = value
            self._parent._dirty = True

        elif name in self.__resolve__:
            fld, klass = self.__resolve__[name]
            if not isinstance(value, klass):
                raise ValueError
            self._parent._data.setdefault(self._name, {})[fld] = value._id
        else:
            raise AttributeError

    def __repr__(self):
        return '%s(**%s)' % (self.__class__.__name__, repr(self._data))

    @property
    def _data(self):
        return self._parent._data.get(self._name)

from abc import ABC
from collections import OrderedDict


class InstanceBase(ABC, OrderedDict):
    fields = []

    def __init__(self, *args, **kwds):
        # Fields defines the allowed data
        assert self.fields, \
            '`fields` is not set in {}'.format(self.__class__.__name__)

        try:
            initial_data = args[0]
        except IndexError:
            super().__init__(*args, **kwds)
            return

        # Verify we're only adding an allowed values
        for field_set in initial_data:
            assert field_set[0] in self.fields, \
                '`{}` is an invalid field.'.format(field_set)

        # Build OrderedDict structure based on `fields` & populate
        data = []
        for field in self.fields:
            try:
                value = list(filter(lambda x: x[0] == field, initial_data))[0][1]
            except IndexError:
                value = None

            data += [(field, value)]

        super().__init__(data, **kwds)

    def __setitem__(self, key, value, **kwargs):

        # Verify we're only adding an allowed value
        assert key in self.fields, '`{}` is an invalid key.'.format(key)

        super().__setitem__(key, value, **kwargs)

    @classmethod
    def factory(cls, *fields):
        # cls.fields = fields
        return type(
            cls.__name__,
            (cls, object),
            {'fields': fields}
        )
        # return cls


class ResourceBase(ABC):
    # response = None
    # raw = None
    data = {}
    fields = []

    instance_class = None
    # instance_class = InstanceBase.factory(fields)

    # def __init__(self):
    #     self.instance_class = InstanceBase.factory(fields)

    # def save_raw(self):
    #     self.raw = self.response.json()

    # def verify_status_code(self, code):
    #     if self.response.status_code != code:
    #         try:
    #             detail = 'Response json: {}'.format(self.response.json())
    #         except json.decoder.JSONDecodeError:
    #             detail = 'Response body: {}'.format(self.response.text)

    #         raise RequestException(
    #             detail=detail,
    #             status_code=self.response.status_code,
    #         )

    def get_instance(self, data):
        if not self.instance_class:
            self.instance_class = InstanceBase.factory(*self.fields)

        # assert self.instance_class.__name__ != 'InstanceBase', \
        #     '`instance_class` is InstanceBase, it must inherit from `InstanceBase`.'

        # assert issubclass(self.instance_class, InstanceBase), \
        #     '`instance_class` must inherit from `InstanceBase`.'

        return self.instance_class(data)

    # def process(self, code):
    #     self.verify_status_code(code)
    #     self.save_raw()

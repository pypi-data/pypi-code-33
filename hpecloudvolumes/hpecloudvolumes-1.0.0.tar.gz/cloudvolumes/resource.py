# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.


class Resource:
    __slots__ = ['id', 'attrs', 'collection', '_client']

    def __init__(self, id, attrs=None, client=None, collection=None):
        self.id = id
        self.attrs = {} if attrs is None else attrs
        self.collection = collection

        self._client = client

    def reload(self):
        self.attrs = self.collection.get(self.id).attrs

    def __repr__(self):
        if 'name' in self.attrs:
            return f"<{self.__class__.__name__}(id={self.id}, name={self.attrs['name']})>"
        else:
            return f"<{self.__class__.__name__}(id={self.id})>"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self):
        return hash(f"{self.__class__.__name__}:{self.id}")


class Collection:
    __slots__ = ['resource', 'resource_type', '_client']

    def __init__(self, client=None):
        # self.resource_type = resource_type
        self._client = client

    def get(self, id=None, **kwargs):
        if id is not None:
            obj = getattr(self._client, f"get_{self.resource_type}_ident")(id)
            return self.resource(obj['id'], obj['attributes'], client=self._client, collection=self)
        elif kwargs is not None:
            objs = getattr(self._client, f"get_{self.resource_type}")(filters=','.join([f'{k}={v}' for k, v in kwargs.items()]))
            if len(objs) == 0:
                return None
            else:
                return self.resource(objs[0]['id'], objs[0]['attributes'], client=self._client, collection=self)

    def list(self, **kwargs):
        objs = getattr(self._client, f"get_{self.resource_type}")(filters=','.join([f'{k}={v}' for k, v in kwargs.items()]))
        return [self.resource(obj['id'], obj['attributes'], client=self._client, collection=self) for obj in objs]

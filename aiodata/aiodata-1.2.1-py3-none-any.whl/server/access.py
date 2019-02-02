import operator
import functools


__all__ = ('Access',)


class Access:

    __slots__ = ('_objects', '_model')

    def __init__(self, objects, model):

        self._objects = objects

        self._model = model

    @property
    def name(self):

        return self._model._meta.name

    @property
    def primary(self):

        return self._model._meta.primary_key.field_names

    def query(self, keys):

        fields = (getattr(self._model, key) for key in self.primary)

        associations = (field == key for (field, key) in zip(fields, keys))

        action = functools.reduce(operator.and_, associations)

        return action

    def _execute(self, action, keys):

        if keys:

            query = self.query(keys)

            action = action.where(query)

        return self._objects.execute(action)

    def _revert(self, data):

        for (key, value) in data.items():

            if not value is None:

                continue

            data[key] = getattr(self._model, key).default

    def get(self, keys):

        action = self._model.select().dicts()

        return self._execute(action, keys)

    def create(self, keys, **data):

        self._revert(data)

        extra = zip(self.primary, keys)

        data.update(extra)

        action = self._model.insert(**data)

        return self._execute(action, None)

    def update(self, keys, **data):

        self._revert(data)

        action = self._model.update(**data)

        return self._execute(action, keys)

    def delete(self, keys):

        action = self._model.delete()

        return self._execute(action, keys)

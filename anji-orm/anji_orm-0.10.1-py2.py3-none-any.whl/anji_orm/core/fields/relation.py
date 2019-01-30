import asyncio
import collections.abc
import functools
import operator
import typing

from toolz import itertoolz

from .base import Field
from ..register import orm_register
from ..utils import ensure_element


if typing.TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['LinkField', 'ListLinkField']


def set_to_cache(model_class, model_id, result):
    if isinstance(result, asyncio.Future):
        result = result.result()
    orm_register.shared.relation_cache[model_class._table][model_id] = result


def get_model_and_load_to_cache(model_class, model_id):
    if orm_register.async_mode:
        result: asyncio.Task = asyncio.ensure_future(model_class.async_get(model_id))
        result.add_done_callback(functools.partial(set_to_cache, model_class, model_id))
    else:
        result = model_class.get(model_id)
        set_to_cache(model_class, model_id, result)
    return result


class LinkField(Field):

    __slots__ = ('_table_name', '_model_class', '_allow_none')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._table_name: str
        self._model_class: typing.Type['Model']
        self._allow_none: bool = False

    # pylint: disable=no-member
    @Field.param_type.setter  # type: ignore
    def param_type(self, value: typing.Type['Model']) -> None:
        self._param_type = value
        self._model_class = value
        if hasattr(self._model_class, '__origin__'):
            if self._model_class.__origin__ is typing.Union:  # type: ignore
                self._allow_none = itertoolz.count(filter(lambda x: isinstance(None, x), self._model_class.__args__)) > 0  # type: ignore
                self._model_class = itertoolz.first(filter(operator.truth, self._model_class.__args__))  # type: ignore
        self._table_name = self._model_class._table

    def real_value(self, model_record):
        return model_record._values.get(self.name)

    def can_be(self, target_type: typing.Type) -> bool:
        if hasattr(target_type, '__origin__') and target_type.__origin__ is not None:
            target_type = target_type.__origin__
        if issubclass(str, target_type):
            return True
        return False

    def __set__(self, instance, value) -> None:
        if not (isinstance(value, str) or (value is None and self._allow_none)):
            raise ValueError(f'Field {self.name} value should have by valid database id instead of {value}')
        instance._values[self.name] = orm_register.backend_adapter.ensure_compatibility(value)

    def __get__(self, instance, instance_type):
        if instance is None:
            return self._get_query_row_for_type(instance_type)
        model_id = instance._values.get(self.name)
        result = orm_register.shared.relation_cache[self._table_name].get(model_id)
        if result is None:
            if model_id is not None:
                result = get_model_and_load_to_cache(self._model_class, model_id)
        return result


class ProxyModelList(collections.abc.MutableSequence, collections.abc.AsyncIterator, collections.abc.Iterator):  # pylint: disable=too-many-ancestors

    __slots__ = ('internal_list', 'table_name', 'model_class')

    def __init__(self, model_class: typing.Type['Model']) -> None:
        self.internal_list: typing.List[str] = []
        self.model_class = model_class
        self.table_name = model_class._table

    def _get_model_by_record_id(self, record_id: str):
        result = orm_register.shared.relation_cache[self.table_name].get(record_id)
        if result is None:
            result = get_model_and_load_to_cache(self.model_class, record_id)
        return result

    def __getitem__(self, index):
        record_id = self.internal_list[index]
        return self._get_model_by_record_id(record_id)

    def __setitem__(self, index, value):
        from ..model import Model  # pylint: disable=redefined-outer-name

        if isinstance(value, Model):
            value = value.id

        self.internal_list[index] = value

    def __delitem__(self, index):
        del self.internal_list[index]

    def __str__(self) -> str:
        return str(self.internal_list)

    def __repr__(self) -> str:
        return str(self.internal_list)

    def insert(self, index, value):
        from ..model import Model  # pylint: disable=redefined-outer-name

        if isinstance(value, Model):
            value = value.id

        self.internal_list.insert(index, value)

    def __len__(self):
        return len(self.internal_list)

    async def __anext__(self):
        for record_id in self.internal_list:
            yield await ensure_element(self._get_model_by_record_id(record_id))

    def __next__(self):
        for record_id in self.internal_list:
            yield self._get_model_by_record_id(record_id)


class ListLinkField(Field):

    __slots__ = ('_model_class',)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._model_class: typing.Type['Model']

    # pylint: disable=no-member
    @Field.param_type.setter  # type: ignore
    def param_type(self, value) -> None:
        from ..model import Model  # pylint: disable=redefined-outer-name

        self._param_type = list
        self._model_class = value.__args__[0]
        if not issubclass(self._model_class, Model):
            raise TypeError("You should use link list field only with one model class!")

    def real_value(self, model_record):
        return model_record._values.get(self.name).internal_list

    def __get__(self, instance, instance_type):
        if instance is None:
            return self._get_query_row_for_type(instance_type)
        proxy_list = instance._values.get(self.name)
        if proxy_list is None:
            proxy_list = ProxyModelList(self._model_class)
            instance._values[self.name] = proxy_list
        return proxy_list

    def __set__(self, instance, value) -> None:
        if not (isinstance(value, list) or (value is None)):
            raise ValueError(f'Field {self.name} value should have by list of database ids instead of {value}')
        new_proxy_list = ProxyModelList(self._model_class)
        if value is not None:
            new_proxy_list.extend(value)
        instance._values[self.name] = new_proxy_list

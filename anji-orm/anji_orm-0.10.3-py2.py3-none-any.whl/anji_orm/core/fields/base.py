import asyncio
import datetime
import inspect
import functools
import logging
from typing import Type, Any, List, Union, Dict, Optional, Callable, TYPE_CHECKING
import sys

from ..ast.rows import QueryRow, BooleanQueryRow, DictQueryRow
from ..register import orm_register

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'Field', 'compute_field'
]

_log = logging.getLogger(__name__)

DICT_ORIGIN: Type[Any] = Dict
if sys.version[0:3] == '3.7':
    DICT_ORIGIN = dict  # pylint: disable=invalid-name


def _type_check(value: Any, target_type: Type) -> bool:
    if hasattr(target_type, '__args__'):
        if target_type.__origin__ is Union:
            return any(_type_check(value, x) for x in target_type.__args__)
        checking_type = target_type if not hasattr(target_type, '_gorg') else target_type._gorg
        if sys.version[0:3] == '3.7':
            base_result = isinstance(value, checking_type.__origin__)
        else:
            base_result = isinstance(value, checking_type)
        # TODO: process advanced type checking!
        return base_result
    return isinstance(value, target_type)


def _none_factory():
    return None


ROW_TYPE_MAPPING: Dict[Type, Type[QueryRow]] = {
    bool: BooleanQueryRow,
    Dict: DictQueryRow
}


class Field:  # pylint:disable=too-many-instance-attributes

    """
    Base ORM field class. Used to describe base logic and provide unified type check
    """

    _anji_orm_field: bool = True
    _anji_orm_extension: str = 'core'

    __slots__ = (
        'default', 'default_factory', 'description',
        'internal', 'field_marks', 'secondary_index',
        # Service or calculate fields
        'name', '_param_type', '_query_row_factory', '_query_row_cache'
    )

    def __init__(
            self, default: Any = None, default_factory: Optional[Callable] = None,
            description: str = '', internal: bool = False, field_marks: Optional[List[str]] = None,
            secondary_index: bool = False) -> None:
        """
        Init function for ORM fields. Provide parameter checks with assertion

        :param default: Field default value, should be strict value. Default value is None.
        :param default_factory: Function without params, that return required default
        :param description: Field description, mostly used for automatic generated commands. Default value is empty string.
        :param internal: If true, this field used only in internal logic. Default value is False.
        :param field_marks: Additional field marks, to use in internal logic. Default value is None.
        :param bool secondary_index: If true, ORM will build secondary_index on this field. Default value is False.
        """
        # Setup fields
        if not ((default is None) or (default_factory is None)):
            raise ValueError("Cannot use field with default and default_factory, please, choose one")
        self.default = default
        self.default_factory = default_factory or _none_factory
        self.description = description
        self.internal = internal
        self.field_marks = field_marks
        self.secondary_index = secondary_index
        self._query_row_cache: Dict[Type, QueryRow] = {}
        # Name will be set by Model Metaclass, by :code:`__set_name__`
        # when field list be fetched
        self.name: str
        self._query_row_factory: Callable[[str, bool, Type], QueryRow]
        self._param_type: Type

    @property
    def param_type(self) -> Type:
        return self._param_type

    @param_type.setter
    def param_type(self, value: Type) -> None:
        self._param_type = value

    def __set_name__(self, owner, name) -> None:
        self.name = name
        target_type = self.param_type
        # Special check for Optinal case
        if hasattr(self.param_type, '__origin__') and self.param_type.__origin__ is Union:
            none_type = type(None)
            real_params = [x for x in self.param_type.__args__ if x is not none_type]  # type: ignore
            if len(real_params) == 1:
                target_type = real_params[0]
        self._query_row_factory = ROW_TYPE_MAPPING.get(target_type, QueryRow)

    def get_default(self):
        if self.default_factory is _none_factory:
            return self.default
        return self.default_factory()

    def real_value(self, model_record):
        """
        Based on __get__ method, but can be used to split overrided __get__ method
        like for LinkField from real infomration
        """
        return self.__get__(model_record, model_record.__class__)

    def _get_query_row_for_type(self, instance_type) -> QueryRow:
        if instance_type in self._query_row_cache:
            return self._query_row_cache[instance_type]
        query_row = self._query_row_factory(  # type: ignore
            self.name, secondary_index=self.secondary_index,
            model_ref=instance_type
        )
        self._query_row_cache[instance_type] = query_row
        return query_row

    def __get__(self, instance, instance_type):
        if instance is None:
            return self._get_query_row_for_type(instance_type)
        return instance._values[self.name]

    def __set__(self, instance, value) -> None:
        if not _type_check(value, self.param_type):
            raise ValueError(f'Field {self.name} value should have {str(self.param_type)} type instead of {value}')
        instance._values[self.name] = orm_register.backend_adapter.ensure_compatibility(value)

    @property
    def is_setable(self) -> bool:
        return True

    def can_be(self, target_type: Type) -> bool:
        if hasattr(target_type, '__origin__'):
            if target_type.__origin__ is DICT_ORIGIN and target_type.__args__:
                return False
            target_type = target_type.__origin__
        if hasattr(self.param_type, '__origin__'):
            if self.param_type.__origin__ is Union:
                if sys.version[0:3] == '3.7':
                    return any(
                        issubclass(
                            x if not hasattr(x, '__origin__')
                            else x.__origin__, target_type
                        ) for x in self.param_type.__args__
                    )
                return any(issubclass(x, target_type) for x in self.param_type.__args__)
            if self.param_type.__origin__ is not None:
                return issubclass(self.param_type.__origin__, target_type)
        return issubclass(self.param_type, target_type)


class ComputeField(Field):

    __slots__ = ('compute_function', 'cacheable', 'stored')

    def __init__(
            self, compute_function, cacheable: bool = False,
            stored: bool = False, **kwargs) -> None:
        """
        :param compute_function: Make field computable and use this function to calculate field value.  Default value is False
        :param cacheable: If false, field value will be recomputed every time on access. Default value is True.
        :param stored: Make field stored in database, if field computed, default False
        """
        super().__init__(**kwargs)
        self.compute_function = compute_function
        self.cacheable = cacheable
        self.stored = stored
        self.param_type = compute_function.__annotations__.get('return', Any)

    def _compute_value(self, instance):
        result = self.compute_function(instance)
        if inspect.iscoroutine(result):
            result = asyncio.ensure_future(result)
        return result

    def _cache_expired(self, instance) -> bool:  # pylint: disable=unused-argument,no-self-use
        return False

    def _after_recompute_hook(self, instance, result) -> None:
        pass

    def _compute_get_logic(self, instance):
        if not self.cacheable:
            return self._compute_value(instance)
        result = instance._values.get(self.name)
        if result is None or self._cache_expired(instance):
            result = self._compute_value(instance)
            instance._values[self.name] = result
            self._after_recompute_hook(instance, result)
        return result

    def __get__(self, instance, instance_type):
        if instance is None:
            return self._get_query_row_for_type(instance_type)
        return self._compute_get_logic(instance)

    def __set__(self, instance, value) -> None:
        if not self.stored:
            raise ValueError("You cannot set value to not stored compute field")
        if not self.cacheable:
            raise ValueError("You cannot properly set not cacheable field")
        if not _type_check(value, self.param_type):
            raise ValueError(f'Field {self.name} value should have {str(self.param_type)} type instead of {value}')
        instance._values[self.name] = value

    @property
    def is_setable(self) -> bool:
        return self.stored and self.cacheable


class TimedComputeField(ComputeField):

    __slots__ = ('expire_delay', )

    def __init__(
            self, compute_function, cacheable: bool = False,
            stored: bool = False, expire_delay: int = 60, **kwargs) -> None:
        """
        :param compute_function: Make field computable and use this function to calculate field value.  Default value is False
        :param cacheable: If false, field value will be recomputed every time on access. Default value is True.
        :param stored: Make field stored in database, if field computed, default False
        :param expire_delay: Delay in seconds, after which stored field will be expired
        """
        super().__init__(compute_function, cacheable=cacheable, stored=stored, **kwargs)
        self.expire_delay = expire_delay

    def _cache_expired(self, instance) -> bool:
        timed_expired = instance.get_extra_info(
            'timed_expired',
            self.name
        )
        return (
            timed_expired is not None and
            timed_expired.astimezone() < datetime.datetime.utcnow().astimezone()
        )

    def _after_recompute_hook(self, instance, result) -> None:
        instance.add_extra_info(
            'timed_expired',
            self.name,
            datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expire_delay)
        )


def compute_field(
        func: Callable = None, **kwargs) -> Callable:
    """
    Very simple method to mark function that should be converted to ComputeField
    """
    if func is None:
        return functools.partial(compute_field, **kwargs)
    func._anji_compute_field = True  # type: ignore
    func._anji_compute_field_kwargs = kwargs  # type: ignore
    if 'expire_delay' in kwargs:
        func._anji_compute_field_class = TimedComputeField  # type: ignore
    else:
        func._anji_compute_field_class = ComputeField  # type: ignore
    return func

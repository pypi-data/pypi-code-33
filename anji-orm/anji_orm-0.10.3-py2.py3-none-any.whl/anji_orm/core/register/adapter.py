import abc
import enum
import functools
import inspect
import typing

if typing.TYPE_CHECKING:
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
    'AbstractBackendAdapter', 'compitability',
    'value_serialization', 'value_deserialization'
]

ValueAdapterFunction = typing.Optional[typing.Callable[[typing.Any, typing.Type], typing.Any]]
AdapterTargetType = typing.Optional[typing.Union[typing.Type, typing.Tuple[typing.Type, ...]]]


def compitability(
        func: ValueAdapterFunction = None,
        target_type: AdapterTargetType = None) -> ValueAdapterFunction:

    if func is None:
        return functools.partial(compitability, target_type=target_type)
    if target_type is None:
        raise ValueError('Please, provide target_type!')
    func.__compitability__ = target_type  # type: ignore
    return func


def value_serialization(
        func: ValueAdapterFunction = None,
        target_type: AdapterTargetType = None) -> ValueAdapterFunction:

    if func is None:
        return functools.partial(value_serialization, target_type=target_type)
    if target_type is None:
        raise ValueError('Please, provide target_type!')
    func.__serialization__ = target_type  # type: ignore
    return func


def value_deserialization(
        func: ValueAdapterFunction = None,
        target_type: AdapterTargetType = None) -> ValueAdapterFunction:

    if func is None:
        return functools.partial(value_deserialization, target_type=target_type)
    if target_type is None:
        raise ValueError('Please, provide target_type!')
    func.__deserialization__ = target_type  # type: ignore
    return func


class AbstractBackendAdapter(abc.ABC):

    __slots__ = ('adapters', 'adapters_tuples')

    def __init__(self):
        self.adapters = {}
        self.adapters_tuples = {}

        for adapter_type in ('serialization', 'deserialization', 'compitability'):
            self.adapters[adapter_type] = {}
            adapter_functions = inspect.getmembers(
                self,
                predicate=lambda x: inspect.ismethod(x) and hasattr(x, f'__{adapter_type}__')  # pylint: disable=cell-var-from-loop
            )
            for _, adapter_function in adapter_functions:
                adapter_mark = getattr(adapter_function, f'__{adapter_type}__')
                if isinstance(adapter_mark, (list, tuple)):
                    for adapter_single_mark in adapter_mark:
                        self.adapters[adapter_type][adapter_single_mark] = adapter_function
                else:
                    self.adapters[adapter_type][adapter_mark] = adapter_function
            self.adapters_tuples[adapter_type] = tuple(self.adapters[adapter_type].keys())

    def register_serialization(self, target_type: typing.Type, function: typing.Callable[[typing.Any], typing.Any]) -> None:
        self.adapters['serialization'][target_type] = function

    def register_deserialization(self, target_type: typing.Type, function: typing.Callable[[typing.Any], typing.Any]) -> None:
        self.adapters['deserialization'][target_type] = function

    def register_compitability(self, target_type: typing.Type, function: typing.Callable[[typing.Any], typing.Any]) -> None:
        self.adapters['compitability'][target_type] = function

    # pylint: disable=redundant-keyword-arg
    @value_serialization(target_type=enum.Enum)  # type: ignore
    def serialize_enum(self, value):  # pylint: disable=no-self-use
        if value is None:
            return value
        return value.name

    # pylint: disable=redundant-keyword-arg
    @value_deserialization(target_type=enum.Enum)  # type: ignore
    def deserialize_enum(self, value, result_type):  # pylint: disable=no-self-use
        if value is None:
            return value
        if hasattr(result_type, '__origin__') and result_type.__origin__ is typing.Union:
            # Try to search something for enum
            enum_class = next(filter(lambda x: issubclass(x, enum.Enum), result_type.__args__), None)
            if enum_class is not None:
                return getattr(enum_class, value)
            raise TypeError("Cannot find enum ... is this even possible?")
        return getattr(result_type, value)

    def record_dict_serialization(self, record_dict: typing.Dict, model_class: typing.Type['Model']) -> typing.Dict:  # pylint: disable=unused-argument,no-self-use
        return record_dict

    def model_serialization(self, record_dict: typing.Dict, model_class: typing.Type['Model']) -> typing.Dict:
        record_dict = {self.row_name_serialization(k): v for k, v in record_dict.items()}
        record_dict = self.record_dict_serialization(record_dict, model_class)
        for serialization_type, serialization_function in self.adapters['serialization'].items():
            for field_name, field in model_class._fields.items():
                if field.can_be(serialization_type) and field_name in record_dict:
                    record_dict[field_name] = serialization_function(record_dict[field_name])
        return record_dict

    def record_dict_deserialization(self, record_dict: typing.Dict, model_class: typing.Type['Model']) -> typing.Dict:  # pylint: disable=unused-argument,no-self-use
        return record_dict

    def model_deserialization(self, record_dict: typing.Dict, model_class: typing.Type['Model']) -> typing.Dict:
        record_dict = {self.row_name_deserialization(k): v for k, v in record_dict.items()}
        record_dict = self.record_dict_deserialization(record_dict, model_class)
        for deserialization_type, deserialization_function in self.adapters['deserialization'].items():
            for field_name, field in model_class._fields.items():
                if field.can_be(deserialization_type) and field_name in record_dict:
                    record_dict[field_name] = deserialization_function(
                        record_dict[field_name],
                        field.param_type
                    )
        return record_dict

    def fetch_processor(self, record_dict: typing.Dict) -> typing.Tuple[typing.Optional[typing.Dict], typing.Optional[typing.Dict]]:  # pylint: disable=no-self-use
        record_dict = {self.row_name_deserialization(k): v for k, v in record_dict.items()}
        return record_dict, None

    def _search_by_superclass(self, value_type, adapter_type):
        for adapter_class, adapter_function in self.adapters[adapter_type].items():
            if issubclass(value_type, adapter_class):
                return adapter_function
        return None

    def _default_pass_logic(self, value, function_to_call):  # pylint: disable=no-self-use
        if isinstance(value, dict):
            return {function_to_call(k): function_to_call(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return type(value)(function_to_call(x) for x in value)
        return value

    def serialize_value(self, value):
        if isinstance(value, self.adapters_tuples['serialization']):
            serialization_function = self.adapters['serialization'].get(type(value))
            if serialization_function is None:
                serialization_function = self._search_by_superclass(type(value), 'serialization')
            return serialization_function(value)
        return self._default_pass_logic(value, self.serialize_value)

    def deserialize_value(self, value, as_type):
        if issubclass(as_type, self.adapters_tuples['deserialization']):
            deserialization_function = self.adapters['deserialization'].get(as_type)
            if deserialization_function is None:
                deserialization_function = self._search_by_superclass(as_type, 'deserialization')
            return deserialization_function(value, as_type)
        return value

    def ensure_compatibility(self, value):  # pylint: disable=no-self-use
        if isinstance(value, self.adapters_tuples['compitability']):
            compitability_function = self.adapters['compitability'].get(type(value))
            if compitability_function is None:
                compitability_function = self._search_by_superclass(type(value), 'compitability')
            return compitability_function(value)
        return self._default_pass_logic(value, self.ensure_compatibility)

    def row_name_serialization(self, row_name: str) -> str:  # pylint: disable=no-self-use
        return row_name

    def row_name_deserialization(self, row_name: str) -> str:  # pylint: disable=no-self-use
        return row_name
